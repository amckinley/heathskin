using System;

public class LogTailer
{
	public LogTailer()
	{
	}

    public void StartTailer()
    {
        using (StreamReader reader = new StreamReader(new FileStream(fileName,
                     FileMode.Open, FileAccess.Read, FileShare.ReadWrite)))
        {
            //start at the end of the file
            long lastMaxOffset = reader.BaseStream.Length;

            while (true)
            {
                System.Threading.Thread.Sleep(100);

                //if the file size has not changed, idle
                if (reader.BaseStream.Length == lastMaxOffset)
                    continue;

                //seek to the last max offset
                reader.BaseStream.Seek(lastMaxOffset, SeekOrigin.Begin);

                //read out of the file until the EOF
                string line = "";
                while ((line = reader.ReadLine()) != null)
                    Console.WriteLine(line);

                //update the last max offset
                lastMaxOffset = reader.BaseStream.Position;
            }
        }
    }
}
