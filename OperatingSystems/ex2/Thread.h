
#include <string.h>
#include <string>
#include <setjmp.h>
#include <iostream>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <sys/time.h>


#define STACK_SIZE 4096 /* stack size per thread (in bytes) */

#ifndef OS_EX2_THREAD_HPP
#define OS_EX2_THREAD_HPP


class Thread {


private:

    // the thread's envionment information
    sigjmp_buf _env;

    // the thread's id
    int _id;

    // the thread's status: READY. BLOCKED, TERMINATED
    std::string _status;

    // if not terminated then true
    bool _is_alive;

    // how much quanta the thread's has
    int _quanta_count;

    // the thread's function
    void (*_func)(void) ;

    // the thread's number of quanta in run
    int _priority_quanta_length;

    // the thread's stack pointer
    char *_stack;



public:
    /*
     * constructor
     */
    Thread(int id, void (*func)(void), int priority_quanta_length);

    /*
     * destructor
     */
    ~Thread();

    /*
     * id getter
     */
    int get_id();

    /*
     * quanta count getter
     */
    int get_quanta_count();

    /*
     * status getter
     */
    std::string get_status();

    /*
     * status setter
     */
    void set_status(std::string status);

    /*
     * increase quanta by 1 each run
     */
    void increment_quanta();

    /*
     * set quanta length per run
     */
    void set_quanta_length(int quanta_length);

    /*
     * getter of quanta length per run
     */
    int get_quanta_length();

    /*
     * setter is alive to false
     */
    void set_is_alive_false();

    /*
     * getter of is alive
     */
    bool get_is_alive();

    /*
     * getter of environment ok
     */
    sigjmp_buf& get_env();

};
#endif //OS_EX2_THREAD_HPP
