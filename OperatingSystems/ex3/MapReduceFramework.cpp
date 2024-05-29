#include "MapReduceFramework.h"
#include <iostream>
#include <atomic>
#include <algorithm>
#include "Barrier.h"
#include <set>


typedef std::vector<IntermediatePair> IntermediateVec;

typedef struct {
    int thread_id;
    JobHandle job;
    IntermediateVec* thread_k2v2_pair;
    bool is_joined;
} ThreadContext;

struct JobContext{
    int threads_count;
    const MapReduceClient* client;
    const InputVec* inputVec;
    OutputVec* outputVec;
    std::vector<pthread_t>* pthreads_vec;
    std::vector<ThreadContext>* tcontext_vec;
    stage_t* job_state;
    std::atomic<int>* map_index;
    std::atomic<int>* reduce_index;
    Barrier* map_shuffle_barrier;
    pthread_mutex_t* emi2_mutex;
    pthread_mutex_t* emi3_mutex;
    pthread_mutex_t* change_stage_mutex;

    std::atomic<unsigned long>* total_map;
    std::atomic<unsigned long>* total_shuffle;
    std::atomic<unsigned long>* total_reduce;

    std::atomic<unsigned long>* cur_total_map;
    std::atomic<unsigned long>* cur_total_shuffle;
    std::atomic<unsigned long>* cur_total_reduce;

    IntermediateMap* toreduce_map;
    std::vector<K2*> *keys_vec;



};


void shuffle(void* context){
    ThreadContext* thread_c = (ThreadContext*) context;
    JobContext* job_c = (JobContext*) thread_c->job;

    for (auto context : *job_c->tcontext_vec) {
        if (pthread_mutex_lock(job_c->emi2_mutex) != 0) {
            std::cerr << "system error: mutex lock failure" << std::endl;
            exit(1);
        }

        for (auto pair : *context.thread_k2v2_pair) {
            int place_in_map = 0;
            for (auto it = job_c->toreduce_map->begin(); it != job_c->toreduce_map->end(); it++) {
                place_in_map++;
                if (!((*(pair.first)) < (*it->first)) && !((*it->first) < (*(pair.first)))) {
                    (*job_c->toreduce_map)[it->first].push_back(pair.second);
                    break;
                }
            }

            // todo maybe needs size-1
            if (place_in_map == job_c->toreduce_map->size()) {
                (*job_c->toreduce_map)[pair.first].push_back(pair.second);
            }
            (*job_c->cur_total_shuffle)++;
        }
        context.thread_k2v2_pair->clear();
        if (pthread_mutex_unlock(job_c->emi2_mutex) != 0) {
            std::cerr << "system error: mutex unlock failure" << std::endl;
            exit(1);
        }
    }
}

void* monster_func(void* context){
    ThreadContext* thread_c = (ThreadContext*) context;
    JobContext* job_c = (JobContext*) thread_c->job;


    // change the job state to MAP
    *job_c->job_state = MAP_STAGE;
    if (thread_c->thread_id != job_c->threads_count-1) {
        //std::cerr<<"thread id:"<<thread_c->thread_id<<std::endl;

        // run map stage with threads while there are jobs
        InputPair p;
        while (*job_c->map_index < job_c->inputVec->size()) {
            size_t old_value = (*job_c->map_index)++;
            p = (*job_c->inputVec)[old_value];
            job_c->client->map((*job_c->inputVec)[old_value].first, (*job_c->inputVec)[old_value].second, context);
            (*job_c->cur_total_map)++;
        }

    }

    // shuffle part
    else{
        while ((size_t) *job_c->cur_total_map < (size_t) *job_c->total_map) {
            shuffle(context);
        }
        int total_size = 0;
        for (auto context : *job_c->tcontext_vec) {
            total_size += context.thread_k2v2_pair->size();
        }
        *(job_c->total_shuffle) = total_size + (size_t) *(job_c->cur_total_shuffle);
        *job_c->job_state = SHUFFLE_STAGE;
        shuffle(context);
        for (auto it = job_c->toreduce_map->begin(); it != job_c->toreduce_map->end(); ++it) {
            job_c->keys_vec->push_back(it->first);
        }

    }

    job_c->map_shuffle_barrier->barrier();
    *job_c->job_state = REDUCE_STAGE;
    size_t old_value2 = 0;
    *job_c->total_reduce = job_c->toreduce_map->size();

    while(job_c->toreduce_map->size() >(size_t) *job_c->reduce_index){
        old_value2=(*job_c->reduce_index)++;
        job_c->client->reduce((*(job_c->keys_vec))[old_value2],job_c->toreduce_map->at((*(job_c->keys_vec))[old_value2]), context);
        (*job_c->cur_total_reduce)++;
    }
    return context;
}

void emit2 (K2* key, V2* value, void* context){
    ThreadContext* thread_c = (ThreadContext*) context;
    JobContext* job_c = (JobContext*) thread_c->job;

    // add the pair to the thread's vector

    if (pthread_mutex_lock(job_c->emi2_mutex) != 0)
    {
        std::cerr << "system error: mutex lock failure"<< std::endl;
        exit(1);
    }
    thread_c->thread_k2v2_pair->push_back(std::make_pair(key,value));

    if (pthread_mutex_unlock(job_c->emi2_mutex) != 0)
    {
        std::cerr << "system error: mutex unlock failure"<< std::endl;
        exit(1);
    }

}


void emit3 (K3* key, V3* value, void* context){
    ThreadContext* thread_c = (ThreadContext*) context;
    JobContext* job_c = (JobContext*) thread_c->job;

    // add the pair to the thread's vector

    if (pthread_mutex_lock(job_c->emi3_mutex) != 0)
    {
        std::cerr << "system error: mutex lock failure"<< std::endl;
        exit(1);
    }

    job_c->outputVec->emplace_back(key,value);

    if (pthread_mutex_unlock(job_c->emi3_mutex) != 0)
    {
        std::cerr << "system error: mutex unlock failure"<< std::endl;
        exit(1);
    }

}

JobHandle startMapReduceJob(const MapReduceClient& client,
                            const InputVec& inputVec, OutputVec& outputVec,
                            int multiThreadLevel){


    // initializations
    std::vector<pthread_t>* pthreads_vec = new std::vector<pthread_t>((unsigned long) multiThreadLevel);
    std::vector<ThreadContext>* tcontext_vec =  new std::vector<ThreadContext>((unsigned long) multiThreadLevel);
    IntermediateMap* toreduce_map = new IntermediateMap;
    std::vector<K2*> *keys_vec = new std::vector<K2*>;

    auto map_index = new std::atomic<int>(0);
    auto reduce_index = new std::atomic<int>(0);

    auto map_barrier = new Barrier(multiThreadLevel);
    auto emit2_mutex = new pthread_mutex_t;
    auto emit3_mutex = new pthread_mutex_t;
    auto change_stage_mutex = new pthread_mutex_t;


    pthread_mutex_init(emit2_mutex, nullptr);
    pthread_mutex_init(emit3_mutex, nullptr);
    pthread_mutex_init(change_stage_mutex, nullptr);


    auto total_map = new std::atomic<unsigned long>(inputVec.size());
    auto total_shuffle = new std::atomic<unsigned long>(1);
    auto total_reduce = new std::atomic<unsigned long>(1);

    auto cur_total_map = new std::atomic<unsigned long>(0);
    auto cur_total_shuffle = new std::atomic<unsigned long>(0);
    auto cur_total_reduce = new std::atomic<unsigned long>(0);


    stage_t *job_state = new stage_t(UNDEFINED_STAGE);
    JobContext *job_c = new JobContext{multiThreadLevel,&client,&inputVec,&outputVec, pthreads_vec, tcontext_vec,
                                       job_state, map_index,reduce_index, map_barrier, emit2_mutex,
                                       emit3_mutex, change_stage_mutex, total_map, total_shuffle,
                                       total_reduce, cur_total_map, cur_total_shuffle,  cur_total_reduce, toreduce_map,
                                       keys_vec};

    // check memory allocation
    if (job_c == nullptr){
        std::cerr<< "system error: failed allocation" << std::endl;
        // todo check if need deallocate memory
        exit(1);
    }


    // create threads and contexts
    for (int index_thread = 0; index_thread<multiThreadLevel; index_thread++){
        auto in_vec = new IntermediateVec();
        bool is_joined = false;
        (*tcontext_vec)[index_thread] = ThreadContext{index_thread,job_c,in_vec, is_joined};
        int res = pthread_create(&(*pthreads_vec)[index_thread], NULL, &monster_func, &(*tcontext_vec)[index_thread]);
        if (res !=0){
            std::cerr<< "system error: failed pthread_create" << std::endl;
            // todo check if need deallocate memory
            exit(1);
        }
    }
    return (JobHandle) job_c;

}


void waitForJob(JobHandle job){


    // join together threads (wait for each other)
    JobContext* job_c = (JobContext*) job;
    for (int index_thread = 0; index_thread<job_c->threads_count; index_thread++){
        if(!((*job_c->tcontext_vec)[index_thread].is_joined)) {
            int res = pthread_join((*(job_c->pthreads_vec))[index_thread], NULL);
            if (res != 0) {
                std::cerr << "system error: failed pthread_create" << std::endl;
                // todo check if need deallocate memory
                exit(1);
            }
        }
    }

}

void getJobState(JobHandle job, JobState* state){
    auto job_c = (JobContext*) job;
    state->stage = *job_c->job_state;
    if (state->stage == MAP_STAGE){
        if((size_t)job_c->total_map!=0)
        state->percentage = ((float) (*job_c->cur_total_map)/(*job_c->total_map))*100;
    }
    else if (state->stage == SHUFFLE_STAGE){
        //printf("in shuffle stage, cur_total=%d, total=%d \n", (int)(*(job_c->cur_total_shuffle)), (int)(*(job_c->total_shuffle)));
        state->percentage = ((float) (*job_c->cur_total_shuffle)/(*job_c->total_shuffle))*100;
    }
    else if (state->stage == REDUCE_STAGE){
        state->percentage = ((float) (*job_c->cur_total_reduce)/(*job_c->total_reduce))*100;
    }
        // todo check if this is the desired behavior
    else {
        state->percentage = 0;
    }
}





void closeJobHandle(JobHandle job){


    auto job_c = (JobContext*) job;

    waitForJob(job);

    delete job_c->map_shuffle_barrier;

    for (auto t_context : *job_c->tcontext_vec){
        delete t_context.thread_k2v2_pair;
    }

    job_c->tcontext_vec->clear();
    delete job_c->tcontext_vec;

    delete job_c->pthreads_vec;

    delete job_c->total_map;

    delete job_c->total_reduce;

    delete job_c->total_shuffle;

    delete job_c->keys_vec;

    delete job_c->cur_total_map;

    delete job_c->cur_total_reduce;

    delete job_c->cur_total_shuffle;

    delete job_c->map_index;

    delete job_c->reduce_index;

    delete job_c->job_state;

    delete job_c->toreduce_map;



    if (pthread_mutex_destroy((job_c->emi2_mutex)) !=0){
        std::cerr<< "system error: failed mutex destroy" << std::endl;
        // todo check if need deallocate memory
        exit(1);
    }

    delete job_c->emi2_mutex;

    if (pthread_mutex_destroy((job_c->emi3_mutex)) !=0){
        std::cerr<< "system error: failed mutex destroy" << std::endl;
        // todo check if need deallocate memory
        exit(1);
    }

    delete job_c->emi3_mutex;

    if (pthread_mutex_destroy((job_c->change_stage_mutex)) !=0){
        std::cerr<< "system error: failed mutex destroy" << std::endl;
        // todo check if need deallocate memory
        exit(1);
    }

    delete job_c->change_stage_mutex;

    delete job_c;
}