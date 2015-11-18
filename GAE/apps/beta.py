# Copyright 2015 Daniel Neve
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#Google Imports
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

#System Imports
import logging
import os

#Project Imports
import common.storage

class FormHandler( webapp2.RequestHandler ):
	def get( self ):
		submitUrl = "/beta/upload/submit/"
		submitUrl = blobstore.create_upload_url( submitUrl );
		
		path = "templates/upload.html"
		values = \
		{
			'url' : submitUrl
		}
		self.response.write( template.render( path, values ) )
		
		
class UploadHandler( blobstore_handlers.BlobstoreUploadHandler ):
	def post( self ):
		
		existingFile = common.storage.FindBetaKey()
		if existingFile is not None:
			logging.debug( "existingFile: " + str( existingFile ) )
			logging.debug( "existingFile id: " + str( existingFile.id ) )
			blobstore.delete( existingFile.id.key() )
		
		blob_info = self.get_uploads()[ 0 ]
		newFile = common.storage.CreateBetaKey( blob_info.key() )
		newFile.put()
		self.redirect( "/beta/" )

class DownloadHandler( blobstore_handlers.BlobstoreDownloadHandler ):
	def get( self ):
		existingFile = common.storage.FindBetaKey()
		if existingFile is not None:
			if blobstore.get( existingFile.id.key() ):
				self.send_blob( existingFile.id, save_as = True )
			else:
				self.error( 404 )

app = webapp2.WSGIApplication \
(
	[
		webapp2.Route( '/beta/upload/', FormHandler ),
		webapp2.Route( '/beta/upload/submit/', UploadHandler ),
		webapp2.Route( '/beta/download/', DownloadHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
