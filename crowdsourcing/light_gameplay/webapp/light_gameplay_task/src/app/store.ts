
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { configureStore } from '@reduxjs/toolkit'
//REDUCERS
import workerActivityReducer from "../features/workerActivity/workerActivity-slice";

export const store = configureStore({
  reducer: {
    workerActivity: workerActivityReducer,
  },
})


export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
