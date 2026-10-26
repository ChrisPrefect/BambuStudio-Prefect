#ifndef slic3r_PrefectTipPolicy_hpp_
#define slic3r_PrefectTipPolicy_hpp_

namespace Slic3r { namespace Prefect {

// Match semantic types, never translated message text or all Hint/Warning levels.
// Multi-filament/prime-tower warnings also use HintNotificationLevel upstream.
template<class Type, class Level>
constexpr bool suppress_tip_notification(bool hide_tips, Type type, Level level)
{
    if (!hide_tips || level >= Level::SeriousWarningNotificationLevel ||
        level == Level::ProgressBarNotificationLevel)
        return false;
    // This informational compatibility tip is labelled Warning upstream.
    if (type == Type::BBLArcFittingInfo)
        return true;
    if (level >= Level::WarningNotificationLevel)
        return false;
    return type == Type::DidYouKnowHint || type == Type::SimplifySuggestion ||
           (type == Type::CustomNotification && level == Level::HintNotificationLevel);
}

// Only these supplied, localized tutorial texts qualify for the independent
// Helio-advertising switch. Never classify a warning by a text prefix.
template<class Type, class Level, class Text>
bool suppress_helio_tutorial(bool hide_ads, Type type, Level level, const Text& text,
                             const Text& first, const Text& second, const Text& third)
{
    return hide_ads && type == Type::CustomNotification && level == Level::HintNotificationLevel &&
           (text == first || text == second || text == third);
}

struct KeepOtherNotifications {
    template<class Data> bool operator()(const Data&) const { return false; }
};

// Used by both update and render: a live preference change also discards tips
// already open or awaiting a delayed condition, before duplicate activation.
template<class ActiveQueue, class WaitingQueue, class Notification, class Extra = KeepOtherNotifications>
bool discard_suppressed_tips(ActiveQueue& active, WaitingQueue& waiting,
                             Notification*& pending_delete, bool hide_tips, Extra extra = {})
{
    const auto suppressed = [hide_tips, &extra](const auto& notification) {
        if (!notification)
            return false;
        const auto& data = notification->get_data();
        return suppress_tip_notification(hide_tips, data.type, data.level) || extra(data);
    };
    bool removed = false;
    for (auto it = active.begin(); it != active.end();) {
        if (suppressed(*it)) {
            if (pending_delete == it->get())
                pending_delete = nullptr;
            it = active.erase(it);
            removed = true;
        } else {
            ++it;
        }
    }
    for (auto it = waiting.begin(); it != waiting.end();) {
        if (suppressed(it->notification)) {
            it = waiting.erase(it);
            removed = true;
        } else {
            ++it;
        }
    }
    return removed;
}

constexpr bool show_automatic_filament_switch_tip(bool hide_tips, bool show_once)
{
    return !hide_tips && show_once;
}

}} // namespace Slic3r::Prefect
#endif
