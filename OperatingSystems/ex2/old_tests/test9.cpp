/*
 * test2.cpp
 *
 *  Created on: Apr 7, 2015
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

void f (void)
{
    while(1);
}

int main(void)
{
    int arr[1] = {10000};
    if (uthread_init(arr, 1) == -1)
    {
        return 0;
    }
    for (int i = 0; i < 101; i++)
        cout << uthread_spawn(f,0) << endl;

    uthread_terminate(5);

    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;

    uthread_terminate(15);
    uthread_terminate(25);
    uthread_terminate(35);
    uthread_terminate(45);
    uthread_terminate(55);
    uthread_terminate(65);
    uthread_terminate(75);
    uthread_terminate(85);

    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;
    cout << uthread_spawn(f,0) << endl;

    uthread_terminate(0);
    return 0;
}

