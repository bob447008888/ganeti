{-| Module abstracting the node and instance container implementation.

This is currently implemented on top of an 'IntMap', which seems to
give the best performance for our workload.

-}

{-

Copyright (C) 2009 Google Inc.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

-}

module Ganeti.HTools.Container
    (
     -- * Types
     Container
    , Key
     -- * Creation
    , empty
    , fromAssocList
     -- * Query
    , size
    , find
     -- * Update
    , add
    , addTwo
    , remove
    , IntMap.map
    , IntMap.mapAccum
    -- * Conversion
    , elems
    , keys
    -- * Element functions
    , nameOf
    , findByName
    ) where

import qualified Data.IntMap as IntMap

import qualified Ganeti.HTools.Types as T

type Key = IntMap.Key
type Container = IntMap.IntMap

-- | Create an empty container.
empty :: Container a
empty = IntMap.empty

-- | Returns the number of elements in the map.
size :: Container a -> Int
size = IntMap.size

-- | Locate a key in the map (must exist).
find :: Key -> Container a -> a
find k = (IntMap.! k)

-- | Add or update one element to the map.
add :: Key -> a -> Container a -> Container a
add = IntMap.insert

-- | Remove an element from the map.
remove :: Key -> Container a -> Container a
remove = IntMap.delete

-- | Return the list of values in the map.
elems :: Container a -> [a]
elems = IntMap.elems

-- | Return the list of keys in the map.
keys :: Container a -> [Key]
keys = IntMap.keys

-- | Create a map from an association list.
fromAssocList :: [(Key, a)] -> Container a
fromAssocList = IntMap.fromList

-- | Add or update two elements of the map.
addTwo :: Key -> a -> Key -> a -> Container a -> Container a
addTwo k1 v1 k2 v2 = add k1 v1 . add k2 v2

-- | Compute the name of an element in a container.
nameOf :: (T.Element a) => Container a -> Key -> String
nameOf c k = T.nameOf $ find k c

-- | Find an element by name in a Container; this is a very slow function.
findByName :: (T.Element a, Monad m) =>
              Container a -> String -> m a
findByName c n =
    let all_elems = elems c
        result = filter ((n `elem`) . T.allNames) all_elems
    in case result of
         [item] -> return item
         _ -> fail $ "Wrong number of elems found with name " ++ n
