
#include "VirtualMemory.h"
#include "PhysicalMemory.h"
#include <string.h>
#include <stdio.h>

/**
 * @brief evalute physical address from frame and offset
 */
#define TO_PHYSICAL(addr, offset) ((addr * PAGE_SIZE) + offset)
/**
 * @brief add depth to address
 */
#define BUILD_ADRR(addr, offset) ((addr << OFFSET_WIDTH) | offset)
void printTree(char* str, uint64_t currFrame = 0, uint64_t vAddr = 0, int depth = 0)
{
    uint64_t frame = 0;
    bool emptyTable = true;
    char myStr[200] = {0};

    sprintf(myStr, "%s->%lu",str, currFrame);
    if (depth == TABLES_DEPTH)
    {
        printf("%s->[%lu] = %lu\n", str, currFrame, vAddr);
        return;
    }

    for (uint64_t i = 0; i < PAGE_SIZE; i++)
    {
        if(TO_PHYSICAL(currFrame, i) >= RAM_SIZE)
        {
            printf("last %s\n", myStr);
            printf("holy shit: frame:%lu, offset:%lu, depth:%d\n", currFrame, i, depth);
            //continue;
        }

        PMread(TO_PHYSICAL(currFrame, i), (word_t*)&frame);

        if (frame != 0)
        {
            emptyTable = false;
            printTree(myStr, frame, BUILD_ADRR(vAddr, i),  depth + 1);
        }
    }

    if (emptyTable)
    {
        printf("%s|\n", myStr);
    }
}
