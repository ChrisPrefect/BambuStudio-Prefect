#ifndef slic3r_GUI_PrefectPlatePolicy_hpp_
#define slic3r_GUI_PrefectPlatePolicy_hpp_

#include <cstddef>
#include <utility>
#include <vector>

namespace Slic3r { namespace GUI { namespace Prefect {

// Plate ownership belongs to each instance, not to the model's first copy.
// Return stable model/instance IDs before the existing deletion path mutates it.
template<class Model, class BelongsToPlate>
std::vector<std::pair<unsigned int, unsigned int>> plate_instance_ids(
    const Model& model, BelongsToPlate belongs)
{
    std::vector<std::pair<unsigned int, unsigned int>> result;
    for (std::size_t object = 0; object < model.objects.size(); ++object) {
        for (std::size_t instance = 0; instance < model.objects[object]->instances.size(); ++instance) {
            const auto object_id = static_cast<unsigned int>(object);
            const auto instance_id = static_cast<unsigned int>(instance);
            if (belongs(object_id, instance_id))
                result.emplace_back(object_id, instance_id);
        }
    }
    return result;
}

}}} // namespace Slic3r::GUI::Prefect
#endif
