#ifndef slic3r_GUI_PrefectArrangePolicy_hpp_
#define slic3r_GUI_PrefectArrangePolicy_hpp_

#include <cstddef>

namespace Slic3r { namespace GUI { namespace Prefect {

// The forced preference is an effective override. Never overwrite the user's
// original per-mode setting, so disabling it restores upstream behavior live.
inline bool arrange_rotation_enabled(bool force_rotation, bool remembered_rotation)
{
    return force_rotation || remembered_rotation;
}

inline bool auto_arrange_insertion_eligible(bool enabled, std::size_t inserted_objects, bool preserve_layout)
{
    return enabled && inserted_objects > 1 && !preserve_layout;
}

enum class PendingArrangeAction { Stop, Retry, Arrange };

struct PendingArrangeState
{
    bool enabled;
    bool closing;
    bool editable;
    bool same_model;
    bool same_objects;
    bool same_undo_position;
    bool busy;
};

inline PendingArrangeAction pending_arrange_action(const PendingArrangeState &state)
{
    // Invalidated requests must stop even while another operation is busy.
    if (!state.enabled || state.closing || !state.editable || !state.same_model ||
        !state.same_objects || !state.same_undo_position)
        return PendingArrangeAction::Stop;
    return state.busy ? PendingArrangeAction::Retry : PendingArrangeAction::Arrange;
}

}}} // namespace Slic3r::GUI::Prefect
#endif
