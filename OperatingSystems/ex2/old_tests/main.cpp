
#include <cstdio>
#include <cstdlib>
#include "/cs/usr/arielleb/CLionProjects/Operating_Systems/os_ex2/uthreads.h"

#define GRN "\e[32m"
#define RED "\x1B[31m"
#define RESET "\x1B[0m"

void halt()
{
    while (true)
    {}
}

void wait_next_quantum()
{
    int quantum = uthread_get_quantums(uthread_get_tid());
    while (uthread_get_quantums(uthread_get_tid()) == quantum)
    {}
    return;
}

void thread1()
{
    uthread_block(uthread_get_tid());
}

void thread2()
{
    halt();
}

void error()
{
    printf(RED "ERROR - wrong id returned\n" RESET);
    exit(1);
}

int main()
{
    printf(GRN "Test 1:    " RESET);
    fflush(stdout);

    int arr[1] = {10};

    uthread_init(arr, 1);
    if (uthread_spawn(thread1, 0) != 1)
        error();
    if (uthread_spawn(thread2, 0) != 2)
        error();
    if (uthread_spawn(thread2, 0) != 3)
        error();
    if (uthread_spawn(thread1,0) != 4)
        error();
    if (uthread_spawn(thread2,0) != 5)
        error();
    if (uthread_spawn(thread1,0) != 6)
        error();

    uthread_terminate(5);
    if (uthread_spawn(thread1,0) != 5)
        error();


    wait_next_quantum();
    wait_next_quantum();

    uthread_terminate(5);
    if (uthread_spawn(thread1,0) != 5)
        error();

    uthread_terminate(2);
    if (uthread_spawn(thread2,0) != 2)
        error();

    uthread_terminate(3);
    uthread_terminate(4);
    if (uthread_spawn(thread2,0) != 3)
        error();
    if (uthread_spawn(thread1,0) != 4)
        error();

    printf(GRN "SUCCESS\n" RESET);
    uthread_terminate(0);

}