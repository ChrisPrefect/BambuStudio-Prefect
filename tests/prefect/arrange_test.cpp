#include "../../src/slic3r/GUI/PrefectArrangePolicy.hpp"

#include <cassert>
#include <iostream>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using namespace Slic3r::GUI::Prefect;
    assert(arrange_rotation_enabled(true, false));
    assert(arrange_rotation_enabled(true, true));
    assert(!arrange_rotation_enabled(false, false));
    assert(arrange_rotation_enabled(false, true));

    // Opening the toolbar popup arranges exactly once when enabled and idle.
    // Closing it or clicking while busy never starts or queues another job.
    for (int enabled = 0; enabled != 2; ++enabled)
        for (int open = 0; open != 2; ++open)
            for (int ready = 0; ready != 2; ++ready)
                assert(arrange_on_toolbar_open(enabled, open, ready) == (enabled && open && ready));
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
