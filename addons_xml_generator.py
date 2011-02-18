""" addons.xml generator """

import os, md5

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file.
        Must be run from the root of the checked-out repo. Only handles
        single depth folder structure.
    """
    def __init__( self ):
        # generate file
        self._generate_addons_file()
        self._generate_md5_file()
        
    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir( "." )
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder
                if ( not os.path.isdir( addon ) or addon == ".svn" ): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "utf-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_addons_file( addons_xml )

    def _save_addons_file( self, addons_xml ):
        try:
            # write the bytestring to the file
            open( "addons.xml", "w" ).write( addons_xml.encode( "utf-8" ) )
        except Exception, e:
            # oops
            print "An error occurred saving file\n%s" % ( e, )

    def _generate_md5_file( self ):
        try:
            # create a new md5 object
            m = md5.new()
        except Exception, e:
            print "An error occurred creating md5 object\n%s" % (e, )
        else:
            try:
                # update the md5 object with the contents of addons.xml
                m.update(open( "addons.xml").read())
                # write md5 file
                open( "addons.xml.md5", "w" ).write( m.hexdigest() )
            except Exception, e:
                print "An error occured saving md5 file\n%s" % ( e, )

if ( __name__ == "__main__" ):
    # start
    Generator()
