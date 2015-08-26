import os
import glob
import tempfile
import shelve
import time
import uuid
import shutil

import tkMessageBox
import tkFileDialog

def get_table_info(path):
	i,header,rows,cols = 0,None,0,None

	fp = open( path, 'r' )
	for l in fp:
		if l[0] == '#' and header == None:
			header = l.rstrip().split()
			cols = len(header)
		if l[0] != '#' and len(l.rstrip()) > 0:
			r = l.rstrip().split()
			if cols != None and len(r) != cols:
				raise Exception("Error on line %i: number of columns does not match header."%(i))
			elif cols == None:
				cols = len(r)
			rows+=1
		i+=1		
	fp.close()
	
	return header,rows,cols
	
def rescue_attribute_table(w,fp):
	if not tkMessageBox.askyesno("Rescue","Do you wish to save the calculated attribute column anyway?",parent=w):
		return
	tmp = tkFileDialog.asksaveasfilename(title='Save rescued attribute table as:',filetypes=[('Attr',"*.attr"),('Text',"*.txt"),('Table',"*.tbl")],initialfile="rescue.txt",parent=w)
	if(tmp == ''):
		return

	fp.seek(0)
	try:
		out = open(tmp,'w')
		for l in fp:
			out.write(l)
	except:
		tkMessageBox.showerror("Error","Error saving attribute table: %s"%(e),parent=w)
	else:
		out.close()
			
def insert_attribute_column(w,child_fp,col_title):
	"""Append or insert into the existing attribute table the new name,value pairs from the temp attribute table
	
	Note: on an error, notifies the user via dialog box and gives the option to save the temporary attribute table elsewhere.
	
	Args:
		w (PDBAttributeWindow): window calling the function
		child_fp (file pointer): Open file pointer to the temp attribute table
		col_title (string): Name of the column to insert
		
	Returns: None 
	"""
	
	parent_file_path = w.attributeFilePath.get()
	parent_bkup_path = parent_file_path+".%i"%(time.time())
	column_menu = w.attributeFileColMenu["menu"]
	column_index = column_menu.index(w.attributeFileColSel.get())

	w.updateAttributeInfo("Consolidating tables...")
		
	try:
		shutil.move(parent_file_path,parent_bkup_path)
	except Exception as e:
		tkMessageBox.showwarning("Error","Error backing up original attribute table: %s"%(e),parent=w)
		rescue_attribute_table(w,child_fp)
		w.updateAttributeInfo("Error.")
		return
		
	def _handle_error(text,title='Error',e=''):
		try:
			shutil.move(parent_bkup_path,parent_file_path)
		except:
			pass
		tkMessageBox.showerror(title,"%s%s"%(text,e),parent=w)
		rescue_attribute_table(w,child_fp)
		w.updateAttributeInfo("Error.")
			
	# open a temporary db to save attribute data
	# also set up a name-keyed dict to track modified records
	try:
		parent_db = shelve.open( os.path.join(tempfile.gettempdir(),uuid.uuid1().hex), 'c' )
		parent_up = {}
	except Exception as e:
		_handle_error("Error opening temporary database:",e)
		return		
	
	try:
		parent_fp = open(parent_bkup_path,'r')
	except Exception as e:
		_handle_error("Error opening original attribute table for reading:",e)
		return
	
	# write existing attribute table into the temporary database
	header,counter = None,0
	for l in parent_fp:
		counter+=1

		l = l.rstrip()
		
		if len(l) == 0:
			break

		if l[0] == '#' and header == None:
			header = l.split()
		if l[0] != '#' and header != None:
			tmp = l.split()
			try:
				if len(tmp) == 1:
					parent_db[tmp[0]] = []
				else:
					parent_db[tmp[0]] = tmp[1:]
				parent_up[tmp[0]] = False
			except IndexError,KeyError:
				_handle_error("Error reading original attribute table, has malformed entry on line %i."%(counter))
				return
					
	parent_fp.close()	
	
	if header == None:
		_handle_error("Attribute table has missing or malformed column header!")
		return
	
	# header will just be column names now
	header.pop(0)
		
	if column_index > len(header):
		_handle_error("Attribute table has the incorrect number of column headers!")
		return
	elif column_index < len(header):
		header[column_index] = col_title
	else:
		header.append(col_title)

	# rewind the incoming file handle to the beginning
	child_fp.seek(0)
	
	counter = 0
	for l in child_fp:
		counter+=1
		try:
			name,data = l.rstrip().split()
		except Exception as e:
			_handle_error("Error inserting new attribute table data, has malformed entry on line %i."%(counter),e)
			return

		if not parent_db.has_key(name):
			_handle_error("PDB entry \"%s\" on line %i is not in existing attribute table!"%(name,counter))
			return
		else:
			tmp = parent_db[name]
			if column_index == len(header)-1: #because we've added a column header already
				tmp.append(data)
			else:
				tmp[column_index] = data
			parent_db[name] = tmp
			parent_up[name] = True

	# check and make sure we've updated all the parent records	
	for name in parent_up:
		if not parent_up[name]:
			_handle_error("Encountered PDB \"%s\" in the original attribute table that was not in the new table!"%(name))
			return
			
	try:
		parent_fp = open(parent_file_path,'w')
	except Exception as e:
		_handle_error("Error opening original attribute table for writing:",e)
		return

	# extract the combined records from the db and write them to the file			
	parent_fp.write("#pdb\t%s\n"%("\t".join(header)))
	for name in parent_up:
		parent_fp.write("%s\t%s\n"%(name,"\t".join(map(str,parent_db[name]))))
	parent_fp.close()
	parent_db.close()
	
	os.unlink(parent_bkup_path)
	return
			
	