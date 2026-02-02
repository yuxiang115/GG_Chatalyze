
const mongoUri = (process.env.MONGO_URI + '/' + process.env.MONGO_DB_NAME) || "mongodb://localhost:27017/gg_chatalyze";

db = connect(mongoUri);
// Create the matches collection if it doesn't exist
if (!db.getCollectionNames().includes("matches")) {
    db.createCollection("matches");
}