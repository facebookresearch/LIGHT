
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./src/index.tsx",
  output: {
    path: __dirname,
    filename: "build/bundle.js",
  },
  node: {
    net: "empty",
    dns: "empty",
  },
  resolve: {
    alias: {
      react: path.resolve("./node_modules/react"),
    },
    extensions: ['.ts', '.tsx', '.js' ],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        loader: "babel-loader",
        exclude: /node_modules/,
        options: { presets: ["@babel/env", "@babel/preset-react"] },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.tsx?$/,
        loader: 'ts-loader',
        exclude: /node_modules/,
        options: {
          compilerOptions: {
            noEmit: false,
          },
        },
      },
      {
        test: /\.(svg|png|jpe?g|ttf)$/,
        loader: "url-loader",

      },
      {
        test: /\.jpg$/,
        loader: "file-loader",
      },
    ],
  },
};
