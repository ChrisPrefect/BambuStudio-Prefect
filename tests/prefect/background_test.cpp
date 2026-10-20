#include "../../src/slic3r/GUI/PrefectBackgroundPolicy.hpp"

#include <cassert>
#include <iostream>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using namespace Slic3r::GUI::Prefect;
    const BackgroundUpdateState ready { true, true, false, false, false, false, false, false, false };
    assert(background_update_action(ready) == BackgroundUpdateAction::Process);

    // Every blocking lifecycle reason retains a pending update rather than
    // consuming the model or starting a second worker.
    for (int reason = 0; reason < 7; ++reason) {
        auto busy = ready;
        switch (reason) {
        case 0: busy.manual_slice = true; break;
        case 1: busy.exporting = true; break;
        case 2: busy.ui_job = true; break;
        case 3: busy.dragging = true; break;
        case 4: busy.gizmo_editing = true; break;
        case 5: busy.completion_pending = true; break;
        case 6: busy.worker_on_other_plate = true; break;
        }
        assert(background_update_action(busy) == BackgroundUpdateAction::Retry);

        // Turning the feature off or opening G-code must stop retrying even
        // while another operation is busy (the old endless-timer regression).
        busy.enabled = false;
        assert(background_update_action(busy) == BackgroundUpdateAction::ValidateOnly);
        busy.enabled = true;
        busy.project_editable = false;
        assert(background_update_action(busy) == BackgroundUpdateAction::ValidateOnly);
    }

    // Processing the same plate may invalidate/cancel its worker via apply();
    // switching to another running plate must wait for its completion instead.
    auto other_plate = ready;
    other_plate.worker_on_other_plate = true;
    assert(background_update_action(other_plate) == BackgroundUpdateAction::Retry);
    other_plate.worker_on_other_plate = false;
    assert(background_update_action(other_plate) == BackgroundUpdateAction::Process);

    assert(requires_prepared_background_start(true, false, false));
    assert(!requires_prepared_background_start(true, true, false)); // explicit Slice/export
    assert(!requires_prepared_background_start(true, false, true)); // checked timer path
    assert(!requires_prepared_background_start(false, false, false));

    assert(background_script_choice_resolved(false, std::nullopt));
    assert(!background_script_choice_resolved(true, std::nullopt));
    assert(background_script_choice_resolved(true, std::optional<bool>{false})); // execute
    assert(background_script_choice_resolved(true, std::optional<bool>{true}));  // skip
    std::cout << "Background slicing lifecycle policy: all regression checks passed\n";
}
