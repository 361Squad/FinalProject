import recommend
import time


# # example usage
# url = raw_input('url: ')
# uid_test = recommend.get_steamID64(url)
# print "<<PROCESSING UID>>"
# start_time = time.time()
# for row in recommend.recommend(uid_test):
#     print row
# print "Elapsed time: " + str(time.time()-start_time)
# print "------------------"

# unit tests
# uid_list = (76561198048971211,76561198049109177)
# for uid in uid_list:
#   print "<<PROCESSING UID>>"
#   start_time = time.time()
#   for row in recommend.recommend(uid):
#       print row
#   print "Elapsed time: " + str(time.time()-start_time)
#   print "------------------"

uid_list = (76561198040715074,76561198048971211,76561198049109177,76561198039551867,76561198058290543,76561198302802887) # Cameron, Aaron (derpking7), TJ (thunderwaffle), <random_friend> (TheWeedHead), Mark (Solari985)
for uid in uid_list:
    print "<<PROCESSING UID>>"
    start_time = time.time()
    for row in recommend.recommend(uid):
        print row
    print "Elapsed time: " + str(time.time()-start_time)
    print "------------------"

