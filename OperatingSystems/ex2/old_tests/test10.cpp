/*
 * test3.cpp
 *
 *  Created on: Apr 8, 2015
 *      Author: roigreenberg
 */

#include <stdio.h>
#include <setjmp.h>
#include <signal.h>
#include <unistd.h>
#include <sys/time.h>
#include <stdlib.h>
#include <deque>
#include <list>
#include <assert.h>
#include "/cs/usr/arielleb/CLionProjects/Operating_Systems/os_ex2/uthreads.h"

#include <iostream>
using namespace std;

void f(void){}

int main(void)
{
    int arr[1] = {1000000000};
    if (uthread_init(arr,1) == -1)
    {
        return 0;
    }


    uthread_terminate(-1);
    uthread_block(-1);
    uthread_resume(-1);
    uthread_get_quantums(-1);

    uthread_terminate(1);
    uthread_block(1);
    uthread_resume(1);
    uthread_get_quantums(1);

    uthread_block(0);

    uthread_spawn(f,0);
    uthread_terminate(1);

    uthread_terminate(1);
    uthread_block(1);
    uthread_resume(1);
    uthread_get_quantums(1);

    arr[1] = {0};
    uthread_init(arr,1);
    arr[1] = {-5};
    uthread_init(arr, 1);


    uthread_terminate(0);
    return 0;
}

