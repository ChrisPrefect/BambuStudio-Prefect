#include <cassert>
#include <iostream>
#include <map>
#include <string>

#include "../../src/libslic3r/PrefectWorkflowPreferences.hpp"

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

struct StoredPreferences {
    std::map<std::string, std::string> values;
    std::string get(const std::string& key) const {
        const auto found = values.find(key);
        return found == values.end() ? std::string() : found->second;
    }
    void set(const std::string& key, const std::string& value) { values[key] = value; }
    void set_bool(const std::string& key, bool value) { set(key, value ? "true" : "false"); }
};

int main()
{
    using namespace Slic3r::Prefect;
    StoredPreferences fresh;
    set_workflow_defaults(fresh);
    assert(fresh.values.size() == 14);
    assert(fresh.get("background_processing") == "true");
    assert(fresh.get("prefect_arrange_rotation") == "true");
    assert(fresh.get("prefect_arrange_after_import") == "true");
    assert(fresh.get("prefect_arrange_on_click") == "true");
    assert(fresh.get("prefect_hide_helio_ads") == "true");
    assert(fresh.get("prefect_support_interface_menu") == "true");
    assert(fresh.get("prefect_simple_fields_enabled") == "false");
    assert(fresh.get("prefect_workflow_revision") == "2");
    assert(fresh.values.count("prefect_simple_fields") == 0);

    // All user-disabled features survive both defaults and v1 -> v2 migration.
    auto existing = fresh;
    for (auto& value : existing.values)
        if (value.first != "prefect_workflow_revision")
            value.second = "false";
    existing.set("prefect_workflow_revision", "1");
    existing.set("prefect_simple_fields", "some_future_field,layer_height");
    set_workflow_defaults(existing);
    assert(migrate_workflow_preferences(existing, true));
    assert(existing.get("prefect_workflow_revision") == "2");
    for (const auto& value : existing.values)
        if (value.first != "prefect_workflow_revision" && value.first != "prefect_simple_fields")
            assert(value.second == "false");
    assert(existing.get("prefect_simple_fields") == "some_future_field,layer_height");
    assert(!migrate_workflow_preferences(existing, true));

    // A stock profile's explicit background setting is a real user preference.
    StoredPreferences stock;
    set_workflow_defaults(stock); // AppConfig's constructor precedes file merging.
    stock.set_bool("background_processing", false);
    assert(migrate_workflow_preferences(stock, false));
    set_workflow_defaults(stock);
    assert(stock.get("background_processing") == "false");

    // Missing new keys receive defaults; an enabled or intentionally empty
    // Simple field list and future revisions are never discarded or downgraded.
    existing.values.erase("prefect_arrange_rotation");
    existing.values.erase("prefect_arrange_after_import");
    existing.values.erase("prefect_arrange_on_click");
    existing.values.erase("prefect_hide_helio_ads");
    existing.values.erase("prefect_support_interface_menu");
    existing.set_bool("prefect_simple_fields_enabled", true);
    existing.set("prefect_simple_fields", "");
    existing.set("prefect_workflow_revision", "3");
    set_workflow_defaults(existing);
    assert(existing.get("prefect_arrange_rotation") == "true");
    assert(existing.get("prefect_arrange_after_import") == "true");
    assert(existing.get("prefect_arrange_on_click") == "true");
    assert(existing.get("prefect_hide_helio_ads") == "true");
    assert(existing.get("prefect_support_interface_menu") == "true");
    assert(existing.get("prefect_simple_fields_enabled") == "true");
    assert(existing.values.count("prefect_simple_fields") == 1);
    assert(existing.get("prefect_simple_fields").empty());
    assert(!migrate_workflow_preferences(existing, true));
    assert(existing.get("prefect_workflow_revision") == "3");
    std::cout << "Workflow preference migration: all regression checks passed\n";
}
