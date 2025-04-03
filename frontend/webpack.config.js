const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    mode: 'development',
    entry: {
        guest: './src/guest_interface.js',
        dashboard: './src/combined_dashboard.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'dist'),
        clean: true
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './src/templates/guest.html',
            filename: 'guest.html',
            chunks: ['guest']
        }),
        new HtmlWebpackPlugin({
            template: './src/templates/dashboard.html',
            filename: 'dashboard.html',
            chunks: ['dashboard']
        })
    ],
    devServer: {
        static: {
            directory: path.join(__dirname, 'dist')
        },
        compress: true,
        port: 3000,
        open: true,
        hot: true,
        proxy: {
            '/api': 'http://localhost:5000',
            '/socket.io': {
                target: 'http://localhost:5000',
                ws: true
            }
        }
    },
    devtool: 'source-map'
};