from flask import Flask, request, json, Response
from pymongo import MongoClient

class MongoAPI:
    def __init__(self, data):
        self.client = MongoClient("mongodb://localhost:27017/")  
      
        database = data['database']
        collection_con = data['collection_con']
        collection_post = data['collection_post']
        cursor = self.client[database]
        '''For Contact'''
        self.collection = cursor[collection_con]  
        '''For Post'''
        self.collection_post = cursor[collection_post]   
        self.data = data

    def read(self):
        documents = self.collection_con.find({},{"_id": 0 })
        output = [{item: data[item] for item in data } for data in documents]
        
        documents_post = self.collection_post.find({},{"_id": 0 })
        output_post = [{item: data[item] for item in data } for data in documents_post]
        
        return output,output_post

    def write(self, data):
        #log.info('Writing Data')
        new_document = data['Document']
        response_con = self.collection_con.insert_one(new_document)
        response_post = self.collection_post.insert_one(new_document)
        
        output_con = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response_con.inserted_id)}
        
        output_post = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response_post.inserted_id)}     
           
        return output_con, output_post
    
    def update(self, data):
        filt = data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response_con = self.collection_con.update_one(filt, updated_data)
        response_post = self.collection_post.update_one(filt, updated_data)
        
        output_con = {'Status': 'Successfully Updated' if response_con.modified_count > 0 else "Nothing was updated."}
        output_post = {'Status': 'Successfully Updated' if response_post.modified_count > 0 else "Nothing was updated."}
                
        return output_con,output_post

    def delete(self, data):
        filt = data['Filter']
        response_con = self.collection_con.delete_one(filt)
        output_con = {'Status': 'Successfully Deleted' if response_con.deleted_count > 0 else "Document not found."}
        
        response_post = self.collection_post.delete_one(filt)
        output_post = {'Status': 'Successfully Deleted' if response_post.deleted_count > 0 else "Document not found."}
                
        return output_con,output_post


if __name__ == '__main__':
    data = {
        "database": "Blog_test",
        "collection_con": "Contact",
        "collection_post" : "Post",
    }
    mongo_obj = MongoAPI(data)

    print(json.dumps(mongo_obj.read(), indent=4))
    print(len(mongo_obj.read()))