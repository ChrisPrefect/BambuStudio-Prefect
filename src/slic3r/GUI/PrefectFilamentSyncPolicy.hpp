#ifndef slic3r_GUI_PrefectFilamentSyncPolicy_hpp_
#define slic3r_GUI_PrefectFilamentSyncPolicy_hpp_

namespace Slic3r { namespace GUI { namespace Prefect {

enum class FilamentSyncAction { Stop, Retry, Synchronize };

// Kept free of GUI/network dependencies so disconnects, plate jobs and modal states
// can be regression-tested without a printer or the proprietary network plugin.
struct FilamentSyncState
{
    bool enabled;
    bool closing;
    bool selected_device_matches;
    bool project_editable;
    bool online;
    bool printer_profile_matches;
    bool busy;
};

inline FilamentSyncAction filament_sync_action(const FilamentSyncState &state)
{
    if (!state.enabled || state.closing || !state.selected_device_matches || !state.project_editable)
        return FilamentSyncAction::Stop;
    if (!state.online || !state.printer_profile_matches || state.busy)
        return FilamentSyncAction::Retry;
    return FilamentSyncAction::Synchronize;
}

}}} // namespace Slic3r::GUI::Prefect
#endif
