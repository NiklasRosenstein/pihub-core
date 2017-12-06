var path = require('path');
var webpack = require('webpack');

module.exports = {
  entry: './@pihub/core/app.jsx',
  output: {
    publicPath: '/static/',
    path: {{@ output_dir|repr @}},
    filename: 'bundle.js'
  },
  resolve: {
    //modules: [{{@ build_dir|repr @}}, {{@ (build_dir+'/node_modules')|repr @}}]
    modules: [__dirname, 'node_modules'],
    extensions: ['.js', '.jsx']
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2016', 'react']
        }
      },
      { test: /\.css$/, loader: "style-loader!css-loader" },
      { test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/, use: "url-loader" },
      { test: /\.(ttf|eot|svg|png)(\?[\s\S]+)?$/, use: 'file-loader' }
    ]
  }
}
