#include <cassert>
#include <cstdint>
#include <cstdio>
#include <unordered_map>
#include <vector>

#include "VirtualMemory.h"


using page_t = std::vector<word_t>;

extern std::vector<page_t> RAM;
extern std::unordered_map<uint64_t, page_t> swapFile;


int main()
{
    VMwrite(13, 3);
    assert(
            (RAM
             == std::vector<page_t> {{1, 0}, {0, 2}, {0, 3}, {4, 0}, {0, 3}, {0, 0}, {0, 0}, {0, 0}}));
    assert(swapFile.empty());

    word_t value = 0;

    VMread(13, &value);
    assert(3 == value);
    assert(
            (RAM
             == std::vector<page_t> {{1, 0}, {0, 2}, {0, 3}, {4, 0}, {0, 3}, {0, 0}, {0, 0}, {0, 0}}));
    assert(swapFile.empty());

    VMread(6, &value);  // Reading garbage just to fill the paging structures
    assert(0 == value);  // But we know the garbage is actually 0
    assert(
            (RAM
             == std::vector<page_t> {{1, 0}, {5, 2}, {0, 3}, {4, 0}, {0, 3}, {0, 6}, {0, 7}, {0, 0}}));
    assert(swapFile.empty());

    VMread(31, &value);  // Let's read some more garbage
    assert(0 == value);
    assert(
            (RAM
             == std::vector<page_t> {{1, 4}, {5, 0}, {0, 7}, {0, 2}, {0, 3}, {0, 6}, {0, 0}, {0, 0}}));
    assert((swapFile == std::unordered_map<uint64_t, page_t> {{3, {0, 0}}, {6, {0, 3}}}));

    std::puts("Example flow passed");
}