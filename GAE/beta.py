
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

import logging
import storage

class FormHandler( webapp2.RequestHandler ):
	def get( self ):
		submitUrl = "/beta/upload/submit/"
		submitUrl = blobstore.create_upload_url( submitUrl );
		
		path = "./templates/upload.html"
		values = \
		{
			'url' : submitUrl
		}
		self.response.write( template.render( path, values ) )
		
		
class UploadHandler( blobstore_handlers.BlobstoreUploadHandler ):
	def post( self ):
		
		existingFile = storage.FindBetaKey()
		logging.debug( "existingFile: " + str( existingFile ) )
		logging.debug( "existingFile id: " + str( existingFile.id ) )
		if existingFile is not None:
			blobstore.delete( existingFile.id.key() )
		
		blob_info = self.get_uploads()[ 0 ]
		newFile = storage.CreateBetaKey( blob_info.key() )
		newFile.put()
		self.redirect( "/beta" )

class DownloadHandler( blobstore_handlers.BlobstoreDownloadHandler ):
	def get( self ):
		existingFile = storage.FindBetaKey()
		if existingFile is not None:
			if blobstore.get( existingFile.id.key() ):
				self.send_blob( existingFile.id, save_as = True )
			else:
				self.error( 404 )