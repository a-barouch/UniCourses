
# include "VirtualMemory.h"
# include "PhysicalMemory.h"

struct allImportentFramInfo {

    word_t frame_index;
    uint64_t max_dist;
    uint64_t opt3_selected_page;
    uint64_t last_address_in_op3;
    word_t optional_address;
    int max_frame_index;

};
    void clearTable(uint64_t frameIndex)
{
    for (uint64_t i = 0; i < PAGE_SIZE; ++i)
    {
        PMwrite(frameIndex * PAGE_SIZE + i, 0);
    }
}

void VMinitialize()
{
    clearTable(0);
}

uint64_t min(uint64_t a, uint64_t b)
{
    if ( a < b)
    {
        return a;
    }
    return b;
}

uint64_t max(uint64_t a, uint64_t b)
{
    if ( a < b)
    {
        return b;
    }
    return a;
}

int abs(int a)
{
    if ( a <0){
        return -a;
    }
    return a;
}


// the return value is if the first option is the one
int findFreeFrame(uint64_t ignored_frame, int depth, uint64_t last_address, uint64_t cur_frame,
                  uint64_t cur_page, uint64_t p, allImportentFramInfo &frames_info)
{
    bool is_frame_empty = true;
    //check the third option
    if (TABLES_DEPTH == depth){
        uint64_t dist = (uint64_t) abs((int) cur_page - p);
        dist=min(int(dist), (int(NUM_PAGES - dist)));
        if (max(dist, frames_info.max_dist) == dist)
        {
            // we save the current maximal distance
            frames_info.max_dist= dist;

            // we save the address of the current maximal distance
            frames_info.opt3_selected_page = p;

            // we save the parent of the current maximal distance
            frames_info.last_address_in_op3 = last_address;

            // we save the frame of the current maximal distance
            frames_info.frame_index = cur_frame;

        }
    }
    else {
        word_t next_frame = 0;
        word_t physical_addrress;
        for (int i = 0; i < PAGE_SIZE; i++) {
            physical_addrress = cur_frame * PAGE_SIZE + (uint64_t) i;
            PMread(physical_addrress, &next_frame);

            //checks for the second option
            if (next_frame == 0) {
                frames_info.max_frame_index = max(frames_info.max_frame_index, next_frame);
            }
            else{
                is_frame_empty = false;
                if (findFreeFrame(ignored_frame,depth + 1,  physical_addrress,
                                  next_frame, cur_page, p<< OFFSET_WIDTH| (uint64_t) i , frames_info)) {
                    return 1;
                }
                frames_info.max_frame_index = max(frames_info.max_frame_index, next_frame);
            }
        }

        // if the current frame is not the one we are checking and the frame is not empty
        if (cur_frame != ignored_frame) {
            if(is_frame_empty){
                PMwrite(last_address, 0);
                frames_info.optional_address = cur_frame;
                return 1;
            }
        }
    }
    return 0;
}



// find a frame with the three options and returns the address of the place to write in it
word_t find_frame(uint64_t virtualAddress)
{
    word_t last_address = 0;
    word_t address = 0;
    uint64_t cur_frame_physical = 0;
    int last_depth=TABLES_DEPTH-1;

    for (int cur_depth = 0; cur_depth < TABLES_DEPTH; cur_depth++) {

        //calculate cur page from full address
        uint64_t cur_page =  (virtualAddress >> (OFFSET_WIDTH * (TABLES_DEPTH -(uint64_t) cur_depth)));
        cur_page = cur_page & (PAGE_SIZE - 1);
        cur_frame_physical = last_address * PAGE_SIZE + cur_page;
        //check what is in the current address
        PMread(cur_frame_physical,(word_t*)&address);

        if (address == 0){

            // creating a struct that holds the important information of the frames
            allImportentFramInfo frames_info = {0,0,0,0,0,0};

            // running recursive algorithm that includes option 1, 2 and 3
            bool is_first_option=findFreeFrame(last_address, 0, 0, 0,  virtualAddress >> OFFSET_WIDTH, 0, frames_info);

            // 1st option
            if(is_first_option)
            {
                // next frame already has the right value in this case
            }
            //2nd option
            else if (frames_info.max_frame_index < NUM_FRAMES-1){
                frames_info.optional_address  = ++frames_info.max_frame_index;
            }

            //3rd option
            else {
                // is not pointed to the cur address
                frames_info.optional_address  = frames_info.frame_index;
                PMwrite(frames_info.last_address_in_op3, 0);
                PMevict(frames_info.optional_address , frames_info.opt3_selected_page);
            }

            address = frames_info.optional_address ;
            uint64_t FrameToWrite = last_address * PAGE_SIZE + cur_page;
            PMwrite(FrameToWrite, frames_info.optional_address);

            // when we reached an actual page (not a table)
            if (cur_depth == last_depth)
            {
                PMrestore(address , virtualAddress >> OFFSET_WIDTH);
            }
            else{
                clearTable(address);
            }
        }
        last_address = address;
    }
    return address;
}


int VMread(uint64_t virtualAddress, word_t* value) {
    if (VIRTUAL_MEMORY_SIZE <= virtualAddress){
        return 0;
    }
    word_t cur_address = find_frame(virtualAddress);
    PMread(cur_address*PAGE_SIZE+ ((virtualAddress) & (PAGE_SIZE - 1)),value );
    return 1;
}


int VMwrite(uint64_t virtualAddress, word_t value) {
    if (VIRTUAL_MEMORY_SIZE <= virtualAddress){
        return 0;
    }
    word_t cur_address = find_frame(virtualAddress);
    PMwrite(cur_address*PAGE_SIZE+((virtualAddress) & (PAGE_SIZE - 1)),value);
    return 1;
}