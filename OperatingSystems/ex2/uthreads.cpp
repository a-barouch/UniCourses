
#include "uthreads.h"
#include <exception>
#include <new>
#include <deque>
#include <signal.h>
#include <sys/time.h>
#include "Thread.h"



int *quantum_priorities_arr;
int quantum_priorities_arr_size;
sigset_t signal_set;
struct sigaction sig_action;
struct itimerval timer;
Thread *thread_list[MAX_THREAD_NUM];
int quantum_total = 0;
Thread *running_thread;
std::deque<Thread *> ready_threads;



void destruct_when_exit(){
    for (int i = 0; i < MAX_THREAD_NUM; i++) {
        thread_list[i]->~Thread();
    }

    delete(quantum_priorities_arr);
}


int check_tid(int tid) {
    if (tid >= MAX_THREAD_NUM || tid < 0) {
        std::cerr << "thread library error: invalid tid value" << std::endl;
        return -1;
    }

    //  check if thread exists
    if (!thread_list[tid]->get_is_alive()) {
        std::cerr << "thread library error: invalid tid value" << std::endl;
        return -1;
    }
    return 0;
}

void change_mask(bool block) {

    if (sigemptyset(&signal_set)) {
        std::cerr << "system error: error creating empty set" << std::endl;
        destruct_when_exit();
        exit(1);
    }

    if (sigaddset(&signal_set, SIGVTALRM)) {
        std::cerr << "system error: error adding sygnal to set" << std::endl;
        destruct_when_exit();
        exit(1);
    }


    // block SIGTVALRM signal
    if (block) {

        if (sigprocmask(SIG_BLOCK, &signal_set, nullptr)) {
            std::cerr << "system error: sigprocmask error" << std::endl;
            destruct_when_exit();
            exit(1);
        }
    }

    // unblock SIGTVALRM signal
    else {
        if (sigprocmask(SIG_UNBLOCK, &signal_set, nullptr)) {
            std::cerr << "system error: sigprocmask error" << std::endl;
            destruct_when_exit();
            exit(1);
        }
    }
}


int robin_round() {

    change_mask(true);
    Thread *last_thread = running_thread;

    // if last running was not blocked or terminated, add it to ready queue
    if (last_thread->get_status() != "BLOCKED" || !last_thread->get_is_alive()) {
        last_thread->set_status("READY");
        ready_threads.push_back(last_thread);
    }

    Thread *cur_thread = ready_threads.front();
    
    // iterate over ready queue and find threads which are ready and alive ok
    while (!ready_threads.empty()) {
        ready_threads.pop_front();
        if (cur_thread->get_is_alive()) {
            if (cur_thread->get_status() == "READY") {
                break;
            }
        }
        cur_thread = ready_threads.front();
    }

    // make sure that the ready queue has any ready threads
    if (cur_thread == nullptr || (cur_thread->get_is_alive() && !(cur_thread->get_status() == "READY"))) {
        std::cerr << "thread library error: empty ready queue" << std::endl;
        change_mask(false);
        return -1;
    }

    // save current environment of the last running thread
    int ret_val = sigsetjmp(last_thread->get_env(), 1);

    // return to last running thread
    if (ret_val == 1) {
        running_thread = last_thread;
        last_thread->set_status("RUNNING");
        change_mask(false);
        return 0;
    }

    // running thread is the new function
    cur_thread->set_status("RUNNING");
    running_thread = cur_thread;

    // increment quanta of thread and total quanta
    quantum_total += 1;
    cur_thread->increment_quanta();

    timer.it_value.tv_sec = cur_thread->get_quanta_length() / 1000000;
    timer.it_value.tv_usec = cur_thread->get_quanta_length() % 1000000;


    // configure no expire time in intervals after that
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 0;


    if (setitimer(ITIMER_VIRTUAL, &(timer), nullptr)) {
        std::cerr << "system error: set timer failed" << std::endl;
        destruct_when_exit();
        change_mask(false);
        exit(1);
    }

    change_mask(false);
    siglongjmp(cur_thread->get_env(), 1);

}


void sig_action_handler(int sig) {
    robin_round();
}


int uthread_init(int *quantum_usecs, int size) {

    if (size <= 0) {
        std::cerr << "thread library error: non positive size value" << std::endl;
        return -1;
    }
    // check if all usecs are non negative
    for (int i = 0; i < size; i++) {
        if (quantum_usecs[i] <= 0) {
            std::cerr << "thread library error: non positive quantom value" << std::endl;
            return -1;
        }
    }

    change_mask(true);
    // deep copy of the array
    quantum_priorities_arr_size = size;
    try {
        quantum_priorities_arr = new int[quantum_priorities_arr_size];
    }

    catch (std::bad_alloc& ba){
        std::cerr << "system error: bad memory allocation" << std::endl;
        destruct_when_exit();
        change_mask(false);
        exit(1);
    }
    change_mask(false);

    for (int i = 0; i < size ; i ++){
        quantum_priorities_arr[i] = quantum_usecs[i];
    }


    // configure sig_action mask to be an empty set of signals
    if (sigemptyset(&sig_action.sa_mask)) {
        std::cerr << "system error: error in function call" << std::endl;
        destruct_when_exit();
        change_mask(false);
        exit(1);
    }

    // configure sig_action handler for SIGVTALRM (expiration of thread)
    sig_action.sa_handler = &sig_action_handler;
    if (sigaction(SIGVTALRM, &sig_action, nullptr) < 0) {
        std::cerr << "system error: sigaction failed" << std::endl;
    }


    //initialize time to expire of the main function
    timer.it_value.tv_sec = quantum_usecs[0] / 1000000;        // first time interval, seconds part
    timer.it_value.tv_usec = quantum_usecs[0] % 1000000;        // first time interval, microseconds part


    // configure no expire time in intervals after that
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 0;



    // set timer for the main function
    if (setitimer(ITIMER_VIRTUAL, &(timer), nullptr)) {
        std::cerr << "system error: set timer failed" << std::endl;
        destruct_when_exit();
        change_mask(false);
        exit(1);
    }

    for (int i = 0; i < MAX_THREAD_NUM; i++) {
        thread_list[i] = new Thread(i, nullptr, 0);
        thread_list[i]->set_is_alive_false();
    }

    thread_list[0] = new Thread(0, nullptr, quantum_priorities_arr[0]);
    thread_list[0]->increment_quanta();
    running_thread = thread_list[0];
    change_mask(false);
    quantum_total+=1;
    return 0;
}


int uthread_spawn(void (*f)(void), int priority) {
    change_mask(true);
    int new_id = -1;

    if ((priority>=quantum_priorities_arr_size) || (priority<0)){
        std::cerr << "thread library error: invalid priority value" << std::endl;
        change_mask(false);
        return -1;
    }

    if (f == nullptr){
        std::cerr << "thread library error: invalid function given to thread" << std::endl;
        change_mask(false);
        return -1;
    }


    // check if exceeding max number of threads, finding the ID of the new thread
    for (int i = 0; i < MAX_THREAD_NUM; i++) {
        if (!thread_list[i]->get_is_alive()) {
            new_id = i;
            break;
        }
    }

    // if exceeds max number of threads
    if (new_id == -1) {
        std::cerr << "thread library error: exceeding max thread number" << std::endl;
        change_mask(false);
        return -1;
    }

    // else create a new thread object, add to list of threads and to ready list
    Thread *new_thread = new Thread(new_id, f, quantum_priorities_arr[priority]);
    thread_list[new_id] = new_thread;
    ready_threads.push_back(new_thread);

    change_mask(false);
    return new_thread->get_id();
}


int uthread_block(int tid) {
    change_mask(true);
    // check if tid has legal value and is not terminated
    if (check_tid(tid) != 0) {
        change_mask(false);
        return -1;
    }

    if (tid==0){
        std::cerr << "thread library error: cannot block the main value" << std::endl;
        change_mask(false);
        return -1;
    }

    // change thread status to blocked
    thread_list[tid]->set_status("BLOCKED");

    // if running block is blocking itself, switch to another thread
    if (uthread_get_tid() == tid) {
        robin_round();
    }
    change_mask(false);
    return 0;
}


int uthread_resume(int tid) {
    change_mask(true);
    // check if tid has legal value and is not terminated
    if (check_tid(tid) != 0) {
        change_mask(false);
        return -1;
    }


    // check if blocked, only if blocked change to ready and add to ready queue
    if (thread_list[tid]->get_status() == "BLOCKED") {

        // check if the thread exists in the ready threads as blocked, remove it if it does
        for (size_t i = 0; i<ready_threads.size(); i++){
            if (ready_threads[i]->get_id() == tid){
                ready_threads.erase(ready_threads.begin()+i);
                break;
            }
        }
        thread_list[tid]->set_status("READY");
        ready_threads.push_back(thread_list[tid]);
    }
    change_mask(false);
    return 0;
}


int uthread_terminate(int tid) {
    change_mask(true);
    // check if tid has legal value and is not terminated
    if (check_tid(tid) != 0) {
        change_mask(false);
        return -1;
    }


    // terminating the main results in terminating the whole program
    if (tid == 0) {
        destruct_when_exit();
        change_mask(false);
        exit(0);
    }

    // changing thread's status to terminated
    thread_list[tid]->set_status("TERMINATED");
    thread_list[tid]->set_is_alive_false();

    // if terminated thread is the running thread then switch then running thread
    if (tid == uthread_get_tid()) {
        robin_round();
    }
    change_mask(false);
    return 0;

}

int uthread_change_priority(int tid, int priority) {

    // check if priority has legal value
    if (priority < 0 || priority >= quantum_priorities_arr_size) {
        std::cerr << "thread library error: invalid priority value" << std::endl;
        return -1;
    }

    // check if tid has legal value and is not terminated
    if (check_tid(tid) != 0) {
        return -1;
    }

    // change thread quanta according to priority
    thread_list[tid]->set_quanta_length(quantum_priorities_arr[priority]);
    return 0;
}


int uthread_get_tid() {
    return running_thread->get_id();
}


int uthread_get_total_quantums() {
    return quantum_total;
}


int uthread_get_quantums(int tid) {

    // check if tid has legal value and is not terminated
    if (check_tid(tid) != 0) {
        return -1;
    }
    return thread_list[tid]->get_quanta_count();

}
