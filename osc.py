#!/usr/bin/python

# Copyright (C) 2006 Peter Poeml.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.


from osclib import *


def main():

    cmd = sys.argv[1]
    project = package = filename = None
    # try: 
    #     project = sys.argv[2]
    #     package = sys.argv[3]
    #     filename = sys.argv[4]
    # except: 
    #     pass

    if cmd == 'init':
        project = sys.argv[2]
        package = sys.argv[3]
        init_package_dir(project, package, os.path.curdir)
        print 'Initializing %s (Project: %s, Package: %s)' % (os.curdir, project, package)

    elif cmd == 'ls':
        if len(sys.argv) == 2:
            print '\n'.join(get_slash_source())
        if len(sys.argv) == 3:
            project = sys.argv[2]
            print '\n'.join(meta_get_packagelist(project))
        if len(sys.argv) == 4:
            project = sys.argv[2]
            package = sys.argv[3]
            print '\n'.join(meta_get_filelist(project, package))

    elif cmd == 'meta':
        if len(sys.argv) == 4:
            project = sys.argv[2]
            package = sys.argv[3]
            print ''.join(show_package_meta(project, package))
        elif len(sys.argv) == 3:
            project = sys.argv[2]
            print ''.join(show_project_meta(project))

    elif cmd == 'diff':
        wd = os.curdir
        package = store_read_package(wd)
        project = store_read_project(wd)
        if len(sys.argv) > 2:
            filename = sys.argv[2]
        if filename:
            print get_source_file_diff(project, package, filename)
        else:
            d = []
            for filename in meta_get_filelist(project, package):
                d.append(get_source_file_diff(project, package, filename))
            print ''.join(d)
                

    elif cmd == 'co':

        try: 
            project = sys.argv[2]
            package = sys.argv[3]
            filename = sys.argv[4]
        except: 
            pass

        if filename:
            get_source_file(project, package, filename)

        elif package:
            checkout_package(project, package)

        else:
            # all packages
            for package in meta_get_packagelist(project):
                checkout_package(project, package)


    elif cmd == 'st' or cmd == 'status':

        if len(sys.argv) > 2:
            args = sys.argv[2:]
        else:
            args = [ os.curdir ]
        #print args

        for arg in args:

            if os.path.isfile(arg):
                wd = os.path.dirname(arg)
                filenames = [ os.path.basename(arg) ]
            elif os.path.isdir(arg):
                wd = arg
                package = store_read_package(wd)
                project = store_read_project(wd)
                filenames = meta_get_filelist(project, package)

                # add files which are not listed in _meta
                for i in os.listdir(arg):
                    if i not in filenames and i not in exclude_stuff:
                        filenames.insert(0, i)

            os.chdir(wd)

            for filename in filenames:
                s = get_file_status(project, package, filename)
                #if not s.startswith(' '):
                #    print s
                print s


    elif cmd == 'add':
        filenames = sys.argv[2:]
        for filename in filenames:
            localmeta_addfile(filename)
            print 'A   ', filename

    elif cmd == 'addremove':
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        else:
            args = [ os.curdir ]

        for arg in args:

            if os.path.isfile(arg):
                wd = os.path.dirname(arg)
                filenames = [ os.path.basename(arg) ]
            elif os.path.isdir(arg):
                wd = arg
                package = store_read_package(wd)
                project = store_read_project(wd)
                filenames = meta_get_filelist(project, package)

                # add files which are not listed in _meta
                for i in os.listdir(arg):
                    if i not in filenames and i not in exclude_stuff:
                        filenames.insert(0, i)


            for filename in filenames:
                st = get_file_status(project, package, filename)
                if st.startswith('?'):
                    localmeta_addfile(filename)
                    print 'A   ', filename
                elif st.startswith('!'):
                    print 'D   ', filename
                    localmeta_removefile(filename)



    elif cmd == 'ci' or cmd == 'checkin':
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        else:
            args = [ os.curdir ]
        #print args

        for arg in args:

            if os.path.isfile(arg):
                wd = os.path.dirname(arg)
                filenames = [ os.path.basename(arg) ]
            elif os.path.isdir(arg):
                wd = arg
                package = store_read_package(wd)
                project = store_read_project(wd)
                filenames = meta_get_filelist(project, package)

                # add files which are not listed in _meta
                for i in os.listdir(arg):
                    if i not in filenames and i not in exclude_stuff:
                        filenames.insert(0, i)

            os.chdir(wd)

            files_to_send = []
            files_to_delete = []

            for filename in filenames:
                st = get_file_status(project, package, filename)
                if st.startswith('A') or st.startswith('M'):
                    files_to_send.append(filename)
                    print 'Sending        %s' % filename
                elif st.startswith('D'):
                    files_to_delete.append(filename)
                    print 'Deleting       %s' % filename

            if not files_to_send and not files_to_delete:
                print 'nothing to do'
                sys.exit(0)

            print 'Transmitting file data ', 
            for filename in files_to_send:
                put_source_file(project, package, filename)
                copy_file(filename, os.path.join(store, filename))
            for filename in files_to_delete:
                del_source_file(project, package, filename)
            print
            print 'Transmitting meta data ', 
            put_source_file(project, package, os.path.join(store, '_meta'))

            print
                    

    elif cmd == 'up' or cmd == 'update':

        if len(sys.argv) > 2:
            args = sys.argv[2:]
        else:
            args = [ os.curdir ]
        #print args

        for arg in args:

            if os.path.isfile(arg):
                wd = os.path.dirname(arg)
                filenames = [ os.path.basename(arg) ]
            elif os.path.isdir(arg):
                wd = arg
                package = store_read_package(wd)
                project = store_read_project(wd)
                filenames = meta_get_filelist(project, package)

                ## add files which are not listed in _meta
                #for i in os.listdir(arg):
                #    if i not in filenames and i not in exclude_stuff:
                #        filenames.insert(0, i)

            os.chdir(wd)
            os.chdir(store)

            for filename in filenames:
                get_source_file(project, package, filename)
                wcfilename = os.path.join(os.pardir, os.path.basename(filename))

                if not os.path.exists(wcfilename):
                    print 'A    %s' % filename
                    copy_file(filename, wcfilename)

                elif dgst(wcfilename) != dgst(filename):
                    print 'U    %s' % filename
                    copy_file(filename, wcfilename)

                else:
                    pass

            # get current meta file
            f = open('_meta', 'w')
            f.write(''.join(show_package_meta(project, package)))
            f.close()

                    


            

    elif cmd == 'rm' or cmd == 'delete':
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        else:
            print '%s requires at least one argument' % cmd
            sys.exit(1)

        for arg in args:

            if os.path.isfile(arg):
                wd = os.path.dirname(arg)
                if not wd: wd = os.curdir
                filenames = [ os.path.basename(arg) ]

            os.chdir(wd)

            for filename in filenames:
                localmeta_removefile(filename)
                print 'D    %s' % filename


    elif cmd == 'id':
        print ''.join(get_user_id(sys.argv[2]))

    elif cmd == 'platforms':
        if project:
            print '\n'.join(get_platforms_of_project(project))
        else:
            print '\n'.join(get_platforms())



    elif cmd == 'results':
        if len(sys.argv) > 4:
            platform = sys.argv[4]
            print ''.join(get_results(project, package, platform))
        else:
            for platform in get_platforms_of_project(project):
                print ''.join(get_results(project, package, platform))
                
    elif cmd == 'log':
        wd = os.curdir
        package = store_read_package(wd)
        project = store_read_project(wd)

        platform = sys.argv[2]
        arch = sys.argv[3]
        print ''.join(get_log(project, package, platform, arch))

    else:
        print "unknown command '%s'" % cmd

if __name__ == '__main__':
    init_basicauth()
    main()

