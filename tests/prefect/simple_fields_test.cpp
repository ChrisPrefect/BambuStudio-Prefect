#include "../../src/slic3r/GUI/PrefectSimpleView.hpp"

#include <cassert>
#include <iostream>
#include <vector>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
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
    std::cout << "Simple field policy: all regression checks passed\n";
}
