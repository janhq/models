const path = require("path");
const webpack = require("webpack");
const fs = require("fs");

function generateModelCatalogs() {
  const combinedJsonArray = [];
  // Define the directory containing your JSON files
  const jsonDirectory = path.resolve(__dirname, "../");

  // Read and combine JSON files
  fs.readdirSync(jsonDirectory).forEach((file) => {
    if (file.endsWith(".json")) {
      const filePath = path.join(jsonDirectory, file);
      const jsonData = require(filePath);
      combinedJsonArray.push(jsonData);
    }
  });
  return combinedJsonArray;
}

module.exports = {
  experiments: { outputModule: true },
  entry: "./index.js",
  mode: "production",
  plugins: [
    new webpack.DefinePlugin({
      MODEL_CATALOGS: JSON.stringify(generateModelCatalogs()),
    }),
  ],
  output: {
    filename: "index.js",
    path: path.resolve(__dirname, "dist"),
    library: { type: "module" },
  },
  resolve: {
    extensions: [".ts", ".js"],
  },
  optimization: {
    minimize: false,
  },
};
