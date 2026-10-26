#include "../../src/slic3r/GUI/PrefectPlatePolicy.hpp"
#include <cassert>
#include <iostream>
#include <set>
#include <vector>

#ifdef NDEBUG
#error "Plate deletion regressions require active assertions."
#endif

struct Object { std::vector<int> instances; };
struct Model { std::vector<Object*> objects; };

int main()
{
    // A shared model has copies on different plates, including an unplaced
    // copy. Neither first-instance ownership nor selecting the whole object
    // is a valid substitute for checking every instance.
    Object shared{{1, 0, -1, 1}}, only_here{{0}}, all_here{{0, 0}}, elsewhere{{1}};
    Model model{{&shared, &only_here, &all_here, &elsewhere}};
    using Id = std::pair<unsigned int, unsigned int>;
    const auto select = [&](int plate) {
        return Slic3r::GUI::Prefect::plate_instance_ids(model,
            [&](unsigned int object, unsigned int instance) {
                return model.objects[object]->instances[instance] == plate;
            });
    };
    const std::vector<Id> expected{{0, 1}, {1, 0}, {2, 0}, {2, 1}};
    const auto current = select(0);
    assert(current == expected);
    const auto other = select(1);
    assert((other == std::vector<Id>{{0, 0}, {0, 3}, {3, 0}}));
    const std::set<Id> untouched(other.begin(), other.end());
    for (const auto& id : current)
        assert(untouched.count(id) == 0);
    assert(select(2).empty());
    assert((shared.instances == std::vector<int>{1, 0, -1, 1}));
    Model empty;
    assert(Slic3r::GUI::Prefect::plate_instance_ids(empty,
        [](unsigned int, unsigned int) { return true; }).empty());
    std::cout << "Current-plate deletion: shared copies and other plates preserved\n";
}
