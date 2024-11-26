from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:


    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")
        
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")
        
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee  
        if isinstance(value, int) and Employee.find_by_id(value):  
            self._employee_id = value
        else:
            raise ValueError("Employee ID must reference an existing Employee")




    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()  


    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        print(f"Saving review: {self.year}, {self.summary}, {self.employee_id}")
        if self.id:
             
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        else:
                
            sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        CONN.commit()


    @classmethod
    def create(cls, year, summary, employee_id):
            """Initialize a new Review instance and save the object to the database."""
            instance = cls(year, summary, employee_id)  
            instance.save()  
            return instance  

   
    @classmethod
    def instance_from_db(cls, row):
            """Return a Review instance from a database row."""
            instance = cls.all.get(row[0])  
            if instance:
                
                instance.year = row[1]
                instance.summary = row[2]
                instance.employee_id = row[3]
            else:
                
                instance = cls(row[1], row[2], row[3], id=row[0])
                cls.all[instance.id] = instance
            return instance


   

    @classmethod
    def find_by_id(cls, id):
            """Return a Review instance by its ID."""
            sql = "SELECT * FROM reviews WHERE id = ?"
            row = CURSOR.execute(sql, (id,)).fetchone()  
            return cls.instance_from_db(row) if row else None  


    def update(self):
            """Update the review's attributes in the database."""
            if not self.id:
                raise ValueError("Review must be saved before updating.")
    
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()


    def delete(self):
            """Delete the review from the database."""
            if not self.id:
                raise ValueError("Review must be saved before deleting.")
            
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()

            
            del type(self).all[self.id]
            self.id = None  


    @classmethod
    def get_all(cls):
        """Return a list of all Review instances in the database."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()  
        return [cls.instance_from_db(row) for row in rows]  


