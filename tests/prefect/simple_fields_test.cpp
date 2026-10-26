#include "../../src/slic3r/GUI/PrefectSimpleView.hpp"

#include <cassert>
#include <iostream>
#include <map>
#include <vector>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

struct StoredConfig {
    std::map<std::string, std::string> app;
    bool get(const std::string& section, const std::string& key, std::string& value) const
    {
        assert(section == "app");
        const auto found = app.find(key);
        value = found == app.end() ? std::string() : found->second;
        return found != app.end();
    }
};

int main()
{
    namespace Policy = Slic3r::GUI::Prefect;
    using Slic3r::GUI::Prefect::SimpleFieldSelection;
    const SimpleFieldSelection fields(" seam_position,layer_height,layer_height, some_future_field, temperature#1, ,\n");
    assert(fields.keys.size() == 4);
    assert(fields.contains("temperature#0"));
    assert(fields.contains("temperature#2"));
    assert(!fields.contains("seam_gap"));
    assert(fields.serialize() == "layer_height,seam_position,some_future_field,temperature");
    assert(SimpleFieldSelection(fields.serialize()).keys == fields.keys);
    // Shared-label rows are shown when any member was listed, including only
    // the second one in a manually edited or migrated configuration.
    const std::vector<std::string> shared_row{"seam_gap", "seam_position"};
    const auto key_of = [](const std::string& key) { return key; };
    assert(fields.contains_any(shared_row.begin(), shared_row.end(), key_of));
    const std::vector<std::string> hidden_row{"seam_gap", "wall_loops"};
    assert(!fields.contains_any(hidden_row.begin(), hidden_row.end(), key_of));

    // Simple print settings follow the user's list, independently of upstream mode.
    assert(fields.visible(false, true, true, true, "seam_position"));
    assert(!fields.visible(true, true, true, true, "seam_gap"));
    // Other modes, printer/filament tabs, and a disabled override follow upstream.
    assert(!fields.visible(false, false, true, true, "seam_position"));
    assert(fields.visible(true, false, true, true, "seam_gap"));
    assert(!fields.visible(false, true, false, true, "seam_position"));
    assert(fields.visible(true, true, false, true, "seam_gap"));
    assert(!fields.visible(false, true, true, false, "seam_position"));
    assert(fields.visible(true, true, true, false, "seam_gap"));

    const SimpleFieldSelection empty;
    assert(SimpleFieldSelection(",#1, ,\n").keys.empty());
    assert(empty.serialize().empty());
    assert(!empty.visible(true, true, true, true, "layer_height"));
    assert(empty.visible(true, true, true, false, "layer_height"));

    // A process restart, language change or printer temporarily lacking a key
    // must preserve stable selected IDs, including an intentional empty list.
    StoredConfig saved;
    SimpleFieldSelection restored("obsolete_in_memory_value");
    assert(!Policy::load_simple_field_selection(saved, restored));
    assert(restored.keys.empty());
    saved.app["prefect_simple_fields"] = "";
    assert(Policy::load_simple_field_selection(saved, restored));
    assert(restored.keys.empty()); // configured empty, never seed defaults again
    saved.app["prefect_simple_fields"] = "bridge_no_support,layer_height,unavailable_future_key";
    assert(Policy::load_simple_field_selection(saved, restored));
    assert(restored.contains("bridge_no_support"));
    assert(restored.contains("unavailable_future_key"));
    const auto stable_selection = restored.serialize();
    saved.app["prefect_simple_fields"] = stable_selection;
    assert(Policy::load_simple_field_selection(saved, restored));
    assert(restored.serialize() == stable_selection);

    for (bool simple : {false, true})
        for (bool flat : {false, true})
            assert(Policy::use_single_simple_list(simple, flat) == (simple && flat));
    // Flattening is independent of the field override: upstream Simple rows
    // and a saved custom list use the same layout switch.
    assert(Policy::use_single_simple_list(true, true));
    assert(fields.visible(true, true, true, false, "upstream_simple_field"));
    assert(!fields.visible(false, true, true, false, "upstream_advanced_field"));

    // Choosing a dependent field changes discoverability, never applicability.
    // The same rule makes the normal-support bridge setting findable in Expert
    // while Tree support is active, without making its ignored value editable.
    for (bool available : {false, true})
        for (bool selected : {false, true})
            for (bool bridge : {false, true}) {
                const auto state = Policy::simple_row_state(available, selected, bridge);
                assert(state.visible == (available || selected || bridge));
                assert(state.applicable == available);
            }
    assert(!Policy::simple_row_state(false, false, false).visible);
    assert(Policy::simple_row_state(false, true, false).visible);
    assert(!Policy::simple_row_state(false, true, false).applicable);
    assert(!Policy::simple_row_state(false, false, true).applicable);
    assert(Policy::simple_row_state(true, true, false).applicable); // prerequisite restored

    std::cout << "Simple field policy: all regression checks passed\n";
}
