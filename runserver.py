from teine import app, dynamo
import os

dynamo.init_dev()

app.debug = True
app.run(
    host='0.0.0.0',
    port=int(os.getenv('PORT', 5000))
)
