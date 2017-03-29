import database
import agent

db = database.Database()
ag = agent.Agent(db)

db.configuration()
frame = "First message"
ag.sendmessage(frame, 1, 1)