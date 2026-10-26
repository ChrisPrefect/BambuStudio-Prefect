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

inline bool arrange_toolbar_enabled(bool can_arrange, bool popup_open)
{
    // A running job must not clear the toolbar's pressed state and close the
    // options popup. Its controls are disabled until another job can start.
    return can_arrange || popup_open;
}

inline bool arrange_on_toolbar_open(bool enabled, bool popup_open, bool can_arrange)
{
    // The toolbar callback also runs when toggling an item off. Closing the
    // popup must never arrange, and a busy worker must never receive a retry.
    return enabled && popup_open && can_arrange;
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
