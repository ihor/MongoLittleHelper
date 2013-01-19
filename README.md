MongoLittleHelper
=================

Simple tool that helps to analyze MongoDB profiling data from system.profile collection

### Usage

Log into your database through the mongo shell and run db.setProfilingLevel(2). Gather profiling data for some time and run db.setProfilingLevel(0) to disable profiling when you’re done. 

Run MongoLittleHelper:
```python mongo-little-helper.py --host=localhost --port=27017 --db=test```

And see aggregated profiling data:
```
Owners
Total inserts: 1, queries: 18, updates: 299
Queries
18 x 453 us	{_id: {$in: [_]}}
Updates
238 x 54 us	{{_id: _}, {$set: {money: _, cars: _}}}
61 x 99 us	{{_id: _}, {$set: {money: _, sales: _}}}

Cars
Total inserts: 3, queries: 116, updates: 2
Queries
21 x 307 us	{_id: {$in: [_]}}
37 x 178 us	{miles: _, price: _}
58 x 11 us	{_id: _}
Updates
2 x 392 us	{{_id: _}, {$set: {left: _, price: _}}}
```

If you like, you can also drop the system.profile collection afterwards.
