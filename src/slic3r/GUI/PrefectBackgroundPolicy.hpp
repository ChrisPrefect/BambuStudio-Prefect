#ifndef slic3r_GUI_PrefectBackgroundPolicy_hpp_
#define slic3r_GUI_PrefectBackgroundPolicy_hpp_

#include <optional>

namespace Slic3r { namespace GUI { namespace Prefect {

enum class BackgroundUpdateAction { ValidateOnly, Retry, Process };

struct BackgroundUpdateState
{
    bool enabled;
    bool project_editable;
    bool manual_slice;
    bool exporting;
    bool ui_job;
    bool dragging;
    bool gizmo_editing;
    bool completion_pending;
    bool worker_on_other_plate;
};

// This is the policy used by the live timer, kept independent of wxWidgets and
// Print so lifecycle/plate regression cases can run without the full GUI build.
inline BackgroundUpdateAction background_update_action(const BackgroundUpdateState &state)
{
    if (!state.enabled || !state.project_editable)
        return BackgroundUpdateAction::ValidateOnly;
    if (state.manual_slice || state.exporting || state.ui_job || state.dragging ||
        state.gizmo_editing || state.completion_pending || state.worker_on_other_plate)
        return BackgroundUpdateAction::Retry;
    return BackgroundUpdateAction::Process;
}

inline bool requires_prepared_background_start(bool enabled, bool forced, bool prepared)
{
    return enabled && !forced && !prepared;
}

inline bool background_script_choice_resolved(bool has_scripts, const std::optional<bool> &skip_choice)
{
    // An engaged false means "execute", not "no decision".
    return !has_scripts || skip_choice.has_value();
}

}}} // namespace Slic3r::GUI::Prefect
#endif
