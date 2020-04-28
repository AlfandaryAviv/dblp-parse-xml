import xml.etree.ElementTree as ET
import csv
import re
import os
#
# def Unescape(input_path,filename):
#     print('Unescaping ' + filename)
#     text=''
#     replacebles = ['&Ouml;','&ouml;','&Auml;','&auml;','&Uuml;','&uuml;','&szlig;','&oslash;','&aelig;']
#     f = open(input_path+filename+'.xml', "r")
#     num_lines = len([0 for r in f])
#     f.close()
#     f = open(input_path+filename+'.xml', "r")
#     for i, line in enumerate(f):
        
    #     percent = int(i/num_lines*100)
    #     if not percent%5:
    #         print(percent)
    #     newString = line
    #     for r in replacebles:
    #         newString =newString.replace(r,'')
    #     text+=newString
    # f.close()
    # pathname = input_path+ filename + '_new.xml'
    # f = open(pathname,'w')
    # f.write(text)
    # f.close()

class Xml2Txt(object):
    def __init__(self, input_path, min_year, max_year, file_name):
        self.min_year = min_year
        self.max_year = max_year
        self.input_path = input_path
        self.file_name = file_name
        # self.dir = "C:\\Users\\Shuliya\\Desktop\\Lab\\xml2txt\\Temp\\"
        self.dir = "./"
        self.id2author =[]
        self.author2id = {}
        self.label2id = self.create_label_dict()
        self.authors_pairs = {} # dict of authors tuples -> dict of years -> dict of labelid -> num of total articles
        self.authors = [] # list of authors -> dict of years -> dict of labelid -> num of total articles

    def create_label_dict(self):

        labels = dict()

        # data-mining
        for magazine in ["VLDB", "ICDE", "SIGMOD", "PODS", "KDD", "CIKM", "ICDM", "PAKDD", "TKDE"]:
            labels[magazine] = 1
        #networking
        for magazine in ["TCOM", "INFOCOM", "MOBICOM", "SIGCOMM", "VTC", "MobiHoc", "IPSN", "SenSys", "WCNC", "HPDC", "ICNP"]:
            labels[magazine] = 2
        #machine-learning
        for magazine in ["NIPS", "ICML", "UAI", "ICPR", "AAAI", "IJCAI", "ICGA", "FGR", "ISNN","TEC"]:
            labels[magazine] = 3
        #bioinformatics
        for magazine in ["bioinformatics", "BioMED", "ISMB", "RECOMB", "Biocomputing"]:
            labels[magazine] = 4
        #"operating-systems
        for magazine in ["USENIX", "SOSP", "OSDI", "NOSSDAV", "ICDCS", "RTSS", "PODC", "HPCA", "ICS", "HPDC"]:
            labels[magazine] = 5
        #security
        for magazine in ["CRYPTO", "EUROCRYPT", "Security", "CCS", "privacy", "NDSS"]:
            labels[magazine] = 6
        #computer-graphics
        for magazine in ["SIGGRAPH", "SOCG", "I3D"]:
            labels[magazine] = 7
        #computing-theory
        for magazine in ["STOC", "FOCS", "SODA", "ICPP"]:
            labels[magazine] = 8
        #computer-human-interaction
        for magazine in ["CHI", "UIST"]:
            labels[magazine] = 9
        #info-retrieval
        for magazine in ["SIGIR", "WWW", "ISWC", "TREC", "Hypertext"]:
            labels[magazine] = 10
        #software-engineering
        for magazine in ["ICSE"]:
            labels[magazine] = 11
        #computer-vision
        for magazine in ["ICCV", "ECCV", "CVPR"]:
            labels[magazine] = 12
        #computational-linguistics
        for magazine in ["ACL", "linguistics", "COLING"]:
            labels[magazine] = 13
        #verification-testing
        for magazine in ["ITC", "DATE", "CAV"]:
            labels[magazine] = 14

        return labels
        
    def get_author_id(self,author):
        if author not in self.author2id:
            self.id2author.append(author)
            self.author2id[author] = len(self.id2author)
            self.authors.append(dict())
        return self.author2id[author]

    def parse_data(self):
        
        parser = ET.XMLParser()
        # parser.entity["&Ouml;"] = 'o'
        tree = ET.parse(self.input_path, parser=parser)
        print("1")
        root = tree.getroot()

        #TODO: add proceeding
        for article in list(root.findall("./article")) + list(root.findall("./inproceedings")):
            authorid_list=[]
            label_text=""
            year = None
            for proper in article:

                    tag = proper.tag
                    if proper.text:
                        value = proper.text.encode("utf-8")
                        if tag == "author":
                            authorid_list.append(self.get_author_id(value))
                        if tag == "year":
                            try:
                                year= int(value)
                            except ValueError:
                                break
                            if year <self.min_year or year>self.max_year:

                                break
                        if tag == "booktitle" or tag == "journal":
                            label_text = label_text +"\n" + value.decode("utf-8")
        ##                    print(label_text)
                    if not authorid_list or not year:
                        continue
        ##            print(label_text)
                    label = self.get_labelids(label_text)
        ##            print(label)
                    for i in range(len(authorid_list)): # why - 1?
                        authorid1 = authorid_list[i]
                        self.create_author_node(authorid1,year,label)
                        for j in range(i + 1, len(authorid_list)):
                            authorid2 = authorid_list[j]
                            self.create_author_pair(authorid1,authorid2,year,label)

    def create_author_node(self,authorid, year, label):
        author_in_data = authorid-1

        if year not in self.authors[author_in_data]:
            self.authors[author_in_data][year]=dict()

        self.authors[author_in_data][year][label] = self.authors[author_in_data][year].get(label,0)+1

    def create_author_pair(self, author1, author2, year,label):
        if author1 > author2:
            author1, author2 = author2, author1
        authors_tuple = (author1, author2)
        if authors_tuple not in self.authors_pairs:
            self.authors_pairs[authors_tuple] = dict()
        self.authors_pairs[authors_tuple][year] = self.authors_pairs[authors_tuple].get(year, 0) + 1
##        if year not in self.authors_pairs[authors_tuple]:
##            self.authors_pairs[authors_tuple][year] = dict()
            
##        self.authors_pairs[authors_tuple][year][label] = self.authors_pairs[authors_tuple][year].get(label, 0) + 1

    def get_labelids(self,text):
        labels = set()
        pattern = re.compile("\.|/|,|:|;|\ |\[|\]|\{|\}|\(|\)|\<|\>|\"|\'\n\t\r")
        tokens = pattern.split(text)

        for token in tokens:
            current_token = token.lower()
            if current_token in self.label2id:
                labels.add(current_token)
        text = text.strip()
        for key,value in self.label2id.items():
            print(text,key,text==key)
            if text==key:
                return value
        return 0

    def write_nodes(self):
        path = os.path.join(self.dir, self.file_name + "_nodes.csv")
        with open(path, 'w', newline='') as f:
            csv_writer = csv.writer(f)

            for author, year_dict in enumerate(self.authors):

                for year in year_dict:
                    counter = 0
                    for occurances in self.authors[author][year].values():
                        counter += occurances

                    for label in self.authors[author][year]:
                        occurances = self.authors[author][year][label]
                        csv_writer.writerow(
                            [author + 1, year, label, occurances, str(int(occurances / counter * 100)) + "%"])
                        # print([author + 1, year, label, occurances, str(occurances / counter * 100) + "%"])


    def write_edges(self):
        path = os.path.join(self.dir, self.file_name + "_edges.csv")
        with open(path, 'w', newline='') as f:
            csv_writer = csv.writer(f)

            for authors_pair in self.authors_pairs:
                for year in self.authors_pairs[authors_pair]:
                    author1, author2 = authors_pair
                    csv_writer.writerow ([author1,author2,year,self.authors_pairs[authors_pair][year]])


##def main():
##
##
##    xml2txt = Xml2Txt("C:\\Users\\Shuliya\\Desktop\\New folder\\short.xml",1990,2010,"dblp14092019")
##    xml2txt.parse_data()
##    xml2txt.write_edges()
##    xml2txt.write_nodes()
##
##if __name__ == '__main__':
##    main()
# Unescape("C:\\Users\\Shuliya\\Desktop\\Lab\\xml2txt\\Temp\\","dblp")
xml2txt = Xml2Txt("./dblp.xml",1990,2010,"dblp24092019")
#xml2txt = Xml2Txt("C:\\Users\\Shuliya\\Desktop\\Lab\\xml2txt\\Temp\\dblp.xml",1990,2010,"dblp24092019")
xml2txt.parse_data()
xml2txt.write_edges()
xml2txt.write_nodes()
print("Done!")
