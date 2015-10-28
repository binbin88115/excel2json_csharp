using System;
using System.Collections.Generic;
using SimpleJSON;

namespace Config
{
	public class ConfigTable<T> where T : ConfigItem
	{
		private List<T> m_list = new List<T> ();

		public ConfigTable()
		{
		}

		~ConfigTable()
		{
			m_list.Clear();
		}

		public T Query(int id)
		{
			return Query (a => a.Id == id);
		}
		
		public List<T> QueryArray(int id)
		{
			return m_list.FindAll(a => a.Id == id);
		}
		
		public T Query(Predicate<T> match)
		{
			return m_list.Find(match);
		}
		
		public List<T> QueryArray(Predicate<T> match)
		{
			return m_list.FindAll(match);
		}

		public void ReadFromJson(JSONNode node)
		{
			foreach (JSONNode childNode in node.Children) {
				T item = System.Activator.CreateInstance<T>();
				item.Init(childNode);
				m_list.Add(item);
			}
		}
	}
}