def serialize(rows):
        if type(rows) == list:
            result = []
            for row in rows:
                row_dict = row.__dict__
                row_dict.pop('_sa_instance_state', None)
                result.append(row_dict)
            return result
        else:
            row = rows.__dict__
            row.pop('_sa_instance_state', None)
            return row