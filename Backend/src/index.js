import express from "express"
import serverConfig from "./config/serverConfig.js";
import connectDB from "./config/dbConfig.js";
const app = express();

connectDB().then(() => {
    app.listen(serverConfig.PORT, () => {
        console.log(`Server is running on port ${serverConfig.PORT}`);
    });
});