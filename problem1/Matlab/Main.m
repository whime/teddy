fileFolder=fullfile('E:\teddy\venv\RawData');
dirOutput=dir(fullfile(fileFolder,'*.csv'));
fileNames={dirOutput.name}';
FileN=char(fileNames);
for i=1:size(FileN,1)
    L=size(FileN(i,:),2);
    DeleteData(FileN(i,1:L-4),0.041,180,3600,2,400);
end

