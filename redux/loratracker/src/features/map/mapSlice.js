import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

const initialState = {
  'initialzed': false
}

export const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    initialize: (state) => {
      state.initialized = true;
      console.log('CALLED', state);
    }
  }
});

export const { initialize } = mapSlice.actions;

export default mapSlice.reducer;
