#include "../../src/slic3r/GUI/PrefectTipPolicy.hpp"

#include <cassert>
#include <deque>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

// Same semantic enum interface as NotificationManager, without GUI dependencies.
enum class Type { CustomNotification, DidYouKnowHint, SimplifySuggestion,
                  BBLArcFittingInfo, BBLMultiFilaNoWipeTower, ValidateWarning,
                  SlicingError, BBLPluginInstallHint, BBLCalibExtruderMismatch };
enum class Level { ProgressBarNotificationLevel = 1, HintNotificationLevel,
    RegularNotificationLevel, PrintInfoNotificationLevel, PrintInfoShortNotificationLevel,
    ImportantNotificationLevel, WarningNotificationLevel, SeriousWarningNotificationLevel,
    ErrorNotificationLevel };
struct Data { Type type; Level level; };
struct Notification {
    Data data;
    int id;
    const Data& get_data() const { return data; }
};
struct Waiting {
    std::unique_ptr<Notification> notification;
    std::function<bool()> condition;
};
std::unique_ptr<Notification> make(Type type, Level level, int id)
{
    return std::make_unique<Notification>(Notification{{type, level}, id});
}

int main()
{
    using Slic3r::Prefect::suppress_tip_notification;
    using Slic3r::Prefect::discard_suppressed_tips;
    using Slic3r::Prefect::show_automatic_filament_switch_tip;
    constexpr Type types[] = {Type::CustomNotification, Type::DidYouKnowHint,
        Type::SimplifySuggestion, Type::BBLArcFittingInfo, Type::BBLMultiFilaNoWipeTower,
        Type::ValidateWarning, Type::SlicingError, Type::BBLPluginInstallHint,
        Type::BBLCalibExtruderMismatch};
    constexpr Level levels[] = {Level::ProgressBarNotificationLevel, Level::HintNotificationLevel,
        Level::RegularNotificationLevel, Level::PrintInfoNotificationLevel,
        Level::PrintInfoShortNotificationLevel, Level::ImportantNotificationLevel,
        Level::WarningNotificationLevel, Level::SeriousWarningNotificationLevel,
        Level::ErrorNotificationLevel};
    for (auto type : types) {
        for (auto level : levels)
            assert(!suppress_tip_notification(false, type, level));
        assert(!suppress_tip_notification(true, type, Level::ErrorNotificationLevel));
        assert(!suppress_tip_notification(true, type, Level::SeriousWarningNotificationLevel));
        assert(!suppress_tip_notification(true, type, Level::ProgressBarNotificationLevel));
        if (type != Type::BBLArcFittingInfo)
            assert(!suppress_tip_notification(true, type, Level::WarningNotificationLevel));
    }
    assert(suppress_tip_notification(true, Type::BBLArcFittingInfo, Level::WarningNotificationLevel));
    assert(suppress_tip_notification(true, Type::DidYouKnowHint, Level::HintNotificationLevel));
    assert(suppress_tip_notification(true, Type::SimplifySuggestion, Level::PrintInfoNotificationLevel));
    assert(suppress_tip_notification(true, Type::CustomNotification, Level::HintNotificationLevel));
    assert(!suppress_tip_notification(true, Type::CustomNotification, Level::RegularNotificationLevel));
    assert(!suppress_tip_notification(true, Type::BBLMultiFilaNoWipeTower, Level::HintNotificationLevel));
    assert(!suppress_tip_notification(true, Type::BBLCalibExtruderMismatch, Level::HintNotificationLevel));
    assert(!suppress_tip_notification(true, Type::BBLPluginInstallHint, Level::HintNotificationLevel));

    // Toggle on while an arc tip is open and tips are delayed: erase both queues
    // before any condition/duplicate activation; retain real warnings and order.
    std::deque<std::unique_ptr<Notification>> active;
    active.push_back(make(Type::BBLArcFittingInfo, Level::WarningNotificationLevel, 1));
    active.push_back(make(Type::BBLMultiFilaNoWipeTower, Level::HintNotificationLevel, 2));
    active.push_back(make(Type::SlicingError, Level::ErrorNotificationLevel, 3));
    Notification* pending_delete = active.front().get();
    int callbacks = 0;
    std::vector<Waiting> waiting;
    waiting.push_back({make(Type::CustomNotification, Level::HintNotificationLevel, 4), [&] { ++callbacks; return true; }});
    waiting.push_back({make(Type::ValidateWarning, Level::WarningNotificationLevel, 5), [&] { ++callbacks; return true; }});
    waiting.push_back({make(Type::DidYouKnowHint, Level::HintNotificationLevel, 6), [&] { ++callbacks; return true; }});
    assert(!discard_suppressed_tips(active, waiting, pending_delete, false));
    assert(active.size() == 3 && waiting.size() == 3 && pending_delete == active.front().get());
    assert(discard_suppressed_tips(active, waiting, pending_delete, true));
    assert(active.size() == 2 && active[0]->id == 2 && active[1]->id == 3);
    assert(waiting.size() == 1 && waiting[0].notification->id == 5);
    assert(pending_delete == nullptr && callbacks == 0);
    // Repeated render/update is idempotent; a retained warning's pending pointer survives.
    pending_delete = active.front().get();
    assert(!discard_suppressed_tips(active, waiting, pending_delete, true));
    assert(pending_delete == active.front().get() && callbacks == 0);
    assert(!discard_suppressed_tips(active, waiting, pending_delete, false));
    // Turning off allows future tips, without replaying discarded stale messages.
    assert(!suppress_tip_notification(false, Type::BBLArcFittingInfo, Level::WarningNotificationLevel));
    for (bool show_once : {false, true}) {
        assert(!show_automatic_filament_switch_tip(true, show_once));
        assert(show_automatic_filament_switch_tip(false, show_once) == show_once);
    }
    // F13 is independent of F09: only the three supplied localized Custom+Hint
    // messages qualify. Identical text on a warning/error never qualifies.
    const std::string first = "Localized first tutorial\n\n";
    const std::string second = "Localized second tutorial";
    const std::string third = "Localized third tutorial";
    const std::string foreign = "Unrelated tutorial or status";
    using Slic3r::Prefect::suppress_helio_tutorial;
    for (bool hide_tips : {false, true}) {
        for (bool hide_ads : {false, true}) {
            for (const auto& message : {first, second, third}) {
                assert((suppress_tip_notification(hide_tips, Type::CustomNotification, Level::HintNotificationLevel) ||
                        suppress_helio_tutorial(hide_ads, Type::CustomNotification, Level::HintNotificationLevel,
                                                message, first, second, third)) == (hide_tips || hide_ads));
                assert(!suppress_helio_tutorial(hide_ads, Type::CustomNotification, Level::WarningNotificationLevel,
                                                message, first, second, third));
                assert(!suppress_helio_tutorial(hide_ads, Type::CustomNotification, Level::ErrorNotificationLevel,
                                                message, first, second, third));
            }
            assert(!suppress_helio_tutorial(hide_ads, Type::CustomNotification, Level::HintNotificationLevel,
                                            foreign, first, second, third));
        }
    }
    // Live F13 toggle while F09 is off removes only the known promotion from
    // both queues; unrelated Custom+Hint messages and their pending pointer stay.
    struct TextData { Type type; Level level; std::string text; };
    struct TextNotification { TextData data; const TextData& get_data() const { return data; } };
    struct TextWaiting { std::unique_ptr<TextNotification> notification; };
    std::deque<std::unique_ptr<TextNotification>> text_active;
    std::vector<TextWaiting> text_waiting;
    text_active.push_back(std::make_unique<TextNotification>(TextNotification{{Type::CustomNotification, Level::HintNotificationLevel, first}}));
    text_active.push_back(std::make_unique<TextNotification>(TextNotification{{Type::CustomNotification, Level::HintNotificationLevel, foreign}}));
    text_waiting.push_back({std::make_unique<TextNotification>(TextNotification{{Type::CustomNotification, Level::HintNotificationLevel, third}})});
    text_waiting.push_back({std::make_unique<TextNotification>(TextNotification{{Type::CustomNotification, Level::WarningNotificationLevel, first}})});
    TextNotification* text_pending = text_active[1].get();
    const auto hide_promotion = [&](const TextData& data) {
        return suppress_helio_tutorial(true, data.type, data.level, data.text, first, second, third);
    };
    assert(discard_suppressed_tips(text_active, text_waiting, text_pending, false, hide_promotion));
    assert(text_active.size() == 1 && text_active[0]->data.text == foreign && text_pending == text_active[0].get());
    assert(text_waiting.size() == 1 && text_waiting[0].notification->data.level == Level::WarningNotificationLevel);
    assert(callbacks == 0);
    std::cout << "Notification tips: policy, warning protection and live queue toggle passed\n";
}
