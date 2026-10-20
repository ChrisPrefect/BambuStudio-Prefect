#ifndef slic3r_PrefectSimpleView_hpp_
#define slic3r_PrefectSimpleView_hpp_

// Deliberately independent of wxWidgets and libslic3r: this policy is shared by
// settings rows and the settings search index and has a standalone regression test.
#include <set>
#include <sstream>
#include <string>

namespace Slic3r { namespace GUI { namespace Prefect {

class SimpleFieldSelection
{
public:
    std::set<std::string> keys;

    SimpleFieldSelection() = default;
    explicit SimpleFieldSelection(const std::string& serialized)
    {
        std::istringstream input(serialized);
        std::string key;
        while (std::getline(input, key, ',')) {
            // Option IDs are stable ASCII keys. Accept surrounding whitespace in
            // manually edited configuration without changing the serialized form.
            const auto first = key.find_first_not_of(" \t\r\n");
            if (first == std::string::npos)
                continue;
            const auto last = key.find_last_not_of(" \t\r\n");
            const auto normalized = base_key(key.substr(first, last - first + 1));
            if (!normalized.empty())
                keys.insert(normalized);
        }
    }

    static std::string base_key(const std::string& key)
    {
        return key.substr(0, key.find('#'));
    }

    std::string serialize() const
    {
        std::string serialized;
        for (const auto& key : keys) {
            if (!serialized.empty())
                serialized += ',';
            serialized += key;
        }
        return serialized;
    }

    bool contains(const std::string& key) const
    {
        return keys.count(base_key(key)) != 0;
    }

    template<class Iterator, class KeyOf>
    bool contains_any(Iterator first, Iterator last, KeyOf key_of) const
    {
        for (; first != last; ++first)
            if (contains(key_of(*first)))
                return true;
        return false;
    }

    bool visible(bool upstream_visible, bool is_simple, bool is_print,
                 bool enabled, const std::string& key) const
    {
        return is_simple && is_print && enabled ? contains(key) : upstream_visible;
    }
};

}}} // namespace Slic3r::GUI::Prefect

#endif
