#include "../../src/slic3r/GUI/PrefectArrangePolicy.hpp"

#include <cassert>
#include <iostream>
#include <map>
#include <string>

struct StoredArrangePreferences {
    std::map<std::pair<std::string, std::string>, std::string> values;
    unsigned bool_overload_calls = 0;
    std::string get(const std::string& section, const std::string& key) const {
        const auto it = values.find({section, key});
        return it == values.end() ? std::string() : it->second;
    }
    std::string get(const std::string& key) const { return get("app", key); }
    bool get_bool(const std::string& key) const { return get(key) == "true" || get(key) == "1"; }
    void set(const std::string& section, const std::string& key, const std::string& value) { values[{section, key}] = value; }
    // Match AppConfig's overload set: a const char* would otherwise become true.
    void set(const std::string& section, const std::string& key, bool value) {
        ++bool_overload_calls;
        set(section, key, std::string(value ? "true" : "false"));
    }
    void set(const std::string& key, const std::string& value) { set("app", key, value); }
};

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using namespace Slic3r::GUI::Prefect;
    StoredArrangePreferences old_forced;
    old_forced.set("prefect_arrange_rotation", "true");
    old_forced.set("arrange", "enable_rotation_fff", std::string("0"));
    old_forced.set("arrange", "enable_rotation_fff_seq_print", std::string("0"));
    old_forced.set("arrange", "enable_rotation_sla", std::string("0"));
    old_forced.set("arrange", "min_object_distance_fff", std::string("7.5"));
    assert(migrate_arrange_rotation_defaults(old_forced));
    for (const char* key : {"enable_rotation_fff", "enable_rotation_fff_seq_print", "enable_rotation_sla"})
        assert(old_forced.get("arrange", key) == "1");
    assert(old_forced.get("prefect_arrange_rotation_default_revision") == "1");
    assert(old_forced.get("arrange", "min_object_distance_fff") == "7.5");
    assert(old_forced.bool_overload_calls == 0);

    // Explicitly uncheck after upgrade, reload/refresh, and restart with the
    // same stored profile: the workflow default must never turn it back on.
    old_forced.set("arrange", "enable_rotation_fff", std::string("0"));
    const auto chosen = old_forced.values;
    assert(!migrate_arrange_rotation_defaults(old_forced));
    assert(old_forced.values == chosen);
    auto restarted = old_forced;
    assert(!migrate_arrange_rotation_defaults(restarted));
    assert(!initial_arrange_rotation(restarted.get("arrange", "enable_rotation_fff"), true));
    assert(initial_arrange_rotation(restarted.get("arrange", "enable_rotation_sla"), true));

    // An old disabled F10 keeps the normal legacy/current user choices.
    StoredArrangePreferences old_disabled;
    old_disabled.set("prefect_arrange_rotation", "false");
    old_disabled.set("arrange", "enable_rotation", std::string("0"));
    old_disabled.set("arrange", "enable_rotation_sla", std::string("yes"));
    assert(migrate_arrange_rotation_defaults(old_disabled));
    assert(old_disabled.get("arrange", "enable_rotation_fff").empty());
    assert(old_disabled.get("arrange", "enable_rotation") == "0");
    assert(initial_arrange_rotation(old_disabled.get("arrange", "enable_rotation_sla"), false));
    old_disabled.set("prefect_arrange_rotation_default_revision", "2");
    old_disabled.set("prefect_arrange_rotation", "true");
    const auto future = old_disabled.values;
    assert(!migrate_arrange_rotation_defaults(old_disabled));
    assert(old_disabled.values == future);

    assert(initial_arrange_rotation("", true));
    assert(!initial_arrange_rotation("", false));
    assert(!initial_arrange_rotation("false", true));
    assert(!initial_arrange_rotation("no", true));
    assert(initial_arrange_rotation("true", false));

    // Opening the toolbar popup arranges exactly once when enabled and idle.
    // Closing it or clicking while busy never starts or queues another job.
    assert(manual_arrange_available(true, false, false)); // background slicing is deliberately not a veto
    assert(!manual_arrange_available(false, false, false));
    assert(!manual_arrange_available(true, true, false));
    assert(!manual_arrange_available(true, false, true));
    assert(arrange_on_toolbar_open(true, true, manual_arrange_available(true, false, false)));
    assert(!arrange_on_toolbar_open(true, false, true)); // close/switch toolbar
    assert(!arrange_on_toolbar_open(false, true, true)); // popup-only preference
    assert(!arrange_on_toolbar_open(true, true, false)); // no duplicate while UI job runs
    assert(preserve_arrange_popup_on_click(true, true, "arrange")); // repeated direct icon click
    assert(!preserve_arrange_popup_on_click(true, false, "arrange")); // switch-away / programmatic close
    assert(!preserve_arrange_popup_on_click(true, true, "orient")); // other tools unchanged
    assert(!preserve_arrange_popup_on_click(false, true, "arrange")); // classic toggle when disabled
    assert(arrange_toolbar_enabled(true, false));
    assert(arrange_toolbar_enabled(true, true));
    assert(arrange_toolbar_enabled(false, true)); // popup survives running job
    assert(!arrange_toolbar_enabled(false, false)); // busy cannot open a new popup

    assert(auto_arrange_insertion_eligible(true, 2, false));
    assert(!auto_arrange_insertion_eligible(false, 2, false));
    assert(!auto_arrange_insertion_eligible(true, 0, false));
    assert(!auto_arrange_insertion_eligible(true, 1, false)); // merged multipart / instance paste
    assert(!auto_arrange_insertion_eligible(true, 2, true)); // authored layout / recovery

    const PendingArrangeState ready {true, false, true, true, true, true, false};
    assert(pending_arrange_action(ready) == PendingArrangeAction::Arrange);
    auto busy = ready;
    busy.busy = true;
    assert(pending_arrange_action(busy) == PendingArrangeAction::Retry);
    for (int reason = 0; reason < 6; ++reason) {
        auto invalidated = busy;
        switch (reason) {
        case 0: invalidated.enabled = false; break;
        case 1: invalidated.closing = true; break;
        case 2: invalidated.editable = false; break;
        case 3: invalidated.same_model = false; break;
        case 4: invalidated.same_objects = false; break;
        case 5: invalidated.same_undo_position = false; break;
        }
        assert(pending_arrange_action(invalidated) == PendingArrangeAction::Stop);
    }
    std::cout << "Arrange preference and deferred insertion policy: all regression checks passed\n";
}
