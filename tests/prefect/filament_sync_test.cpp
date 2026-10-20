#include "../../src/slic3r/GUI/PrefectFilamentSyncPolicy.hpp"
#include <cassert>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using namespace Slic3r::GUI::Prefect;
    FilamentSyncState state{true, false, true, true, true, true, false};
    assert(filament_sync_action(state) == FilamentSyncAction::Synchronize);

    // Busy updates must be deferred and become runnable without a second device change.
    state.busy = true;
    assert(filament_sync_action(state) == FilamentSyncAction::Retry);
    state.busy = false;
    state.online = false;
    assert(filament_sync_action(state) == FilamentSyncAction::Retry);
    state.online = true;
    state.printer_profile_matches = false;
    assert(filament_sync_action(state) == FilamentSyncAction::Retry);
    state.printer_profile_matches = true;
    assert(filament_sync_action(state) == FilamentSyncAction::Synchronize);

    // A queued callback must not change another printer, a G-code viewer or a closing app,
    // even if a previous callback was waiting for a job or network connection.
    state.busy = true;
    state.selected_device_matches = false;
    assert(filament_sync_action(state) == FilamentSyncAction::Stop);
    state.selected_device_matches = true;
    state.project_editable = false;
    assert(filament_sync_action(state) == FilamentSyncAction::Stop);
    state.project_editable = true;
    state.closing = true;
    assert(filament_sync_action(state) == FilamentSyncAction::Stop);
    state.closing = false;
    state.enabled = false;
    assert(filament_sync_action(state) == FilamentSyncAction::Stop);
}
