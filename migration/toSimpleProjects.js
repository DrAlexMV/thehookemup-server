/* This mongo script will make databases created before 3/24/15 compatible with
   the latest versions of the server and client.

   To apply, run mongo,
   use <your database name>
   and copy and paste this script in and press enter.
   N.S. 3/24/15
*/

db.Users.find().forEach(function(item) {
	item.projects.forEach(function(proj) {
		proj.startDate = '';
		proj.organization = '';
	});
	db.Users.update({_id: item._id}, {$set: {projects: item.projects}});
});
