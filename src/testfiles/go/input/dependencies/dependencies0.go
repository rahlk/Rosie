/* This file is sourced under MIT license from siddontang/go. This is an example
of block comments in go */

package rpc

import "math"

import (
	"container/list"
	"fmt"
	"reflect"
	"sync"
)

import "testing"

type Client struct { // Client struct
	sync.Mutex

	network string
	addr    string

	maxIdleConns int

	conns *list.List
}

// MakeRpc function
func (c *Client) MakeRpc(rpcName string, fptr interface{}) (err error) {
	defer func() {
		if e := recover(); e != nil {
			err = fmt.Errorf("make rpc error")
		}
	}()

	fn := reflect.ValueOf(fptr).Elem()

	nOut := fn.Type().NumOut()
	if nOut == 0 || fn.Type().Out(nOut-1).Kind() != reflect.Interface {
		err = fmt.Errorf("%s return final output param must be error interface", rpcName)
		return
	}

	_, b := fn.Type().Out(nOut - 1).MethodByName("Error")
	if !b {
		err = fmt.Errorf("%s return final output param must be error interface", rpcName)
		return
	}

	f := func(in []reflect.Value) []reflect.Value {
		return c.call(fn, rpcName, in)
	}

	v := reflect.MakeFunc(fn.Type(), f)
	fn.Set(v)

	return
}
