/* REACT */
import React, { useState } from "react";
import { UserIcon } from '@heroicons/react/solid'
import { UserIcon as UserIconOutline } from '@heroicons/react/outline'

export default function UserBadge({children, level, outline, action}) {
  const bgcolor = action ? 'bg-teal-200' : 'bg-white'
  return (<div className={`px-2 py-2 ${bgcolor} group flex select-none items-center rounded-md p-2`}>
    {outline ? <UserIconOutline className="h-6 w-6 " /> : <UserIcon className="h-6 w-6 " />}
    <div className="inline-block mx-2 flex-auto truncate">
      <p className="text-gray-900 text-xs font-bold">{children}</p>
      <p className="text-gray-600 text-xs">{ level ? `level ${level}` : 'character'}</p>
    </div>
  </div>)
}

