db = connect("mongodb://localhost:27017/my_database");

// Create the matches collection if it doesn't exist
if (!db.getCollectionNames().includes("matches")) {
    db.createCollection("matches");
}